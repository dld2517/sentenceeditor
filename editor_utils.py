#!/usr/bin/env python3
"""
Editor Utilities - Editor-specific helper functions
"""

import string
from ui_utils import Colors


class EditorHelpers:
    """Helper functions for outline editor"""
    
    @staticmethod
    def get_heading_key(index):
        """
        Get heading key for an index (0-based)
        Returns: 'a', 'b', 'c', ... 'z', '#26', '#27', etc.
        """
        if index < 26:
            return string.ascii_lowercase[index]
        else:
            return f"#{index}"
    
    @staticmethod
    def get_subheading_key(heading_key, sub_index):
        """
        Get subheading key
        heading_key: 'a', 'b', etc.
        sub_index: 1-based index
        Returns: 'a1', 'a2', 'b1', etc.
        """
        return f"{heading_key}{sub_index}"
    
    @staticmethod
    def parse_heading_command(cmd):
        """
        Parse a heading command like 'ha', 'ha Introduction', 'ha1', 'ha1 Background'
        Returns: (letter, number, text) or None if invalid
        """
        import re
        match = re.match(r'^h([a-zA-Z])(\d*)(.*)$', cmd, re.IGNORECASE)
        if not match:
            return None
        
        letter = match.group(1).lower()
        number = match.group(2)
        text = match.group(3).strip()
        
        return letter, number, text
    
    @staticmethod
    def build_heading_map(db, project_id):
        """
        Build a map of heading keys to (mc_id, mc_name)
        Returns: {'a': (1, 'Introduction'), 'b': (2, 'Methods'), ...}
        """
        major_categories = db.get_major_categories(project_id)
        heading_map = {}
        
        for idx, (mc_id, mc_name, mc_order) in enumerate(major_categories):
            key = EditorHelpers.get_heading_key(idx)
            heading_map[key] = (mc_id, mc_name)
        
        return heading_map
    
    @staticmethod
    def build_subheading_map(db, project_id, heading_map):
        """
        Build a map of subheading keys to (sc_id, sc_name, mc_id)
        Returns: {'a1': (5, 'Background', 1), 'a2': (6, 'Purpose', 1), ...}
        """
        subheading_map = {}
        
        for heading_key, (mc_id, mc_name) in heading_map.items():
            subcategories = db.get_subcategories(mc_id)
            for sub_idx, (sc_id, sc_name, sc_order) in enumerate(subcategories, 1):
                subheading_key = EditorHelpers.get_subheading_key(heading_key, sub_idx)
                subheading_map[subheading_key] = (sc_id, sc_name, mc_id)
        
        return subheading_map
    
    @staticmethod
    def build_outline_structure(db, project_id):
        """
        Build the complete outline structure
        Returns: {mc_id: {sc_id: [(sentence_id, content), ...]}}
        """
        lines = db.get_all_lines(project_id)
        structure = {}
        
        for sentence_id, mc_id, major_cat, sc_id, subcat, content, mc_order, sc_order, s_order in lines:
            if mc_id not in structure:
                structure[mc_id] = {}
            if sc_id not in structure[mc_id]:
                structure[mc_id][sc_id] = []
            structure[mc_id][sc_id].append((sentence_id, content))
        
        return structure
    
    @staticmethod
    def print_outline(db, project_id, collapsed_headings=None):
        """
        Print the complete outline with collapsible headings
        Returns: (heading_map, subheading_map)
        """
        if collapsed_headings is None:
            collapsed_headings = set()
        
        major_categories = db.get_major_categories(project_id)
        
        if not major_categories:
            print(f"\n{Colors.DIM}(No headings yet - use 'ha <heading name>' to create first heading){Colors.RESET}\n")
            return {}, {}
        
        # Build maps
        heading_map = EditorHelpers.build_heading_map(db, project_id)
        subheading_map = EditorHelpers.build_subheading_map(db, project_id, heading_map)
        structure = EditorHelpers.build_outline_structure(db, project_id)
        
        # Print unified view
        print()
        line_num = 1
        
        for idx, (mc_id, mc_name, mc_order) in enumerate(major_categories):
            letter = EditorHelpers.get_heading_key(idx)
            
            # Check if heading is collapsed
            is_collapsed = letter in collapsed_headings
            
            # Print heading with collapse indicator
            collapse_indicator = f"{Colors.DIM}[+]{Colors.RESET}" if is_collapsed else f"{Colors.DIM}[-]{Colors.RESET}"
            print(f"{collapse_indicator} {Colors.BRIGHT_BLUE}[{letter}]{Colors.RESET} {Colors.BOLD}{Colors.BRIGHT_WHITE}{mc_name}{Colors.RESET}")
            
            # Skip content if collapsed
            if is_collapsed:
                print()
                continue
            
            # Get subcategories for this heading
            subcategories = db.get_subcategories(mc_id)
            
            # Print subheadings and their sentences
            for sub_idx, (sc_id, sc_name, sc_order) in enumerate(subcategories, 1):
                subheading_key = EditorHelpers.get_subheading_key(letter, sub_idx)
                
                # If subcategory has a name, show it
                if sc_name:
                    print(f"  {Colors.CYAN}[{subheading_key}]{Colors.RESET} {Colors.BRIGHT_CYAN}{sc_name}{Colors.RESET}")
                
                # Print sentences under this subcategory
                if mc_id in structure and sc_id in structure[mc_id]:
                    for sentence_id, content in structure[mc_id][sc_id]:
                        print(f"    {Colors.GREEN}[{line_num}]{Colors.RESET} {Colors.BRIGHT_WHITE}{content}{Colors.RESET}")
                        line_num += 1
            
            print()  # Blank line between headings
        
        if line_num == 1:
            print(f"{Colors.DIM}(No content yet - use '+ <text>' to add sentences){Colors.RESET}\n")
        
        return heading_map, subheading_map


class CollapseManager:
    """Manage collapse/expand state for headings"""
    
    def __init__(self):
        self.collapsed = set()
    
    def toggle(self, key):
        """Toggle collapse state for a heading key"""
        if key in self.collapsed:
            self.collapsed.remove(key)
            return False  # Now expanded
        else:
            self.collapsed.add(key)
            return True  # Now collapsed
    
    def is_collapsed(self, key):
        """Check if a heading is collapsed"""
        return key in self.collapsed
    
    def expand_all(self):
        """Expand all headings"""
        self.collapsed.clear()
    
    def collapse_all(self, keys):
        """Collapse all headings"""
        self.collapsed = set(keys)
