#!/usr/bin/env python3
"""
Shared project state management
"""

import os
import json

STATE_FILE = ".project_state.json"


def get_active_project():
    """Get the currently active project ID and name"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                return state.get('project_id'), state.get('project_name')
        except:
            return None, None
    return None, None


def set_active_project(project_id, project_name):
    """Set the currently active project"""
    state = {
        'project_id': project_id,
        'project_name': project_name
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)


def clear_active_project():
    """Clear the active project state"""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
