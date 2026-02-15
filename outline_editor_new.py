def print_outline(editor, project_id):
    """Print the entire outline with headings, subheadings, and sentences in unified view"""
    major_categories = editor.get_major_categories(project_id)
    
    if not major_categories:
        print(f"\n{Colors.DIM}(No headings yet - use 'ha <heading name>' to create first heading){Colors.RESET}\n")
        return {}, {}
    
    heading_map = {}
    subheading_map = {}
    
    # Build maps
    for idx, (mc_id, mc_name, mc_order) in enumerate(major_categories):
        letter = string.ascii_lowercase[idx] if idx < 26 else f"#{idx}"
        heading_map[letter] = (mc_id, mc_name)
        
        subcategories = editor.get_subcategories(mc_id)
        for sub_idx, (sc_id, sc_name, sc_order) in enumerate(subcategories, 1):
            subheading_key = f"{letter}{sub_idx}"
            subheading_map[subheading_key] = (sc_id, sc_name, mc_id)
    
    # Get all lines
    lines = editor.get_all_lines(project_id)
    
    # Build a structure: {mc_id: {sc_id: [sentences]}}
    structure = {}
    for sentence_id, mc_id, major_cat, sc_id, subcat, content, mc_order, sc_order in lines:
        if mc_id not in structure:
            structure[mc_id] = {}
        if sc_id not in structure[mc_id]:
            structure[mc_id][sc_id] = []
        structure[mc_id][sc_id].append((sentence_id, content))
    
    # Print unified view
    print()
    line_num = 1
    
    for idx, (mc_id, mc_name, mc_order) in enumerate(major_categories):
        letter = string.ascii_lowercase[idx] if idx < 26 else f"#{idx}"
        
        # Print heading
        print(f"{Colors.BRIGHT_BLUE}[{letter}]{Colors.RESET} {Colors.BOLD}{Colors.BRIGHT_WHITE}{mc_name}{Colors.RESET}")
        
        # Get subcategories for this heading
        subcategories = editor.get_subcategories(mc_id)
        
        # Print subheadings and their sentences
        for sub_idx, (sc_id, sc_name, sc_order) in enumerate(subcategories, 1):
            subheading_key = f"{letter}{sub_idx}"
            
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
