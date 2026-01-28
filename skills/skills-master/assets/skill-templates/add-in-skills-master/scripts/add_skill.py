import os
import shutil
import argparse
import sys
import re

# Define paths relative to this script
# Script is in .../scripts/add_skill.py
# If run from installed location: skills/add-in-skills-master/scripts/add_skill.py
# If run from templates location: skills/skills-master/assets/skill-templates/add-in-skills-master/scripts/add_skill.py

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Heuristic to find SKILLS_ROOT
# We are looking for the 'skills' directory or 'skills-master' root
# If we are in templates, we are deep nested.

if "assets/skill-templates" in CURRENT_DIR:
    # We are running from inside the templates directory (self-update scenario)
    # CURRENT_DIR = .../skills-master/assets/skill-templates/add-in-skills-master/scripts
    SKILLS_MASTER_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR))))
else:
    # We are running from installed location
    # CURRENT_DIR = .../skills/add-in-skills-master/scripts
    # SKILLS_ROOT = .../skills
    SKILLS_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
    SKILLS_MASTER_DIR = os.path.join(SKILLS_ROOT, "skills-master")

SKILLS_MASTER_TEMPLATES = os.path.join(SKILLS_MASTER_DIR, "assets", "skill-templates")
SKILLS_MASTER_DOC = os.path.join(SKILLS_MASTER_DIR, "SKILL.md")

print(f"DEBUG: CURRENT_DIR={CURRENT_DIR}")
print(f"DEBUG: SKILLS_MASTER_DIR={SKILLS_MASTER_DIR}")
print(f"DEBUG: SKILLS_MASTER_TEMPLATES={SKILLS_MASTER_TEMPLATES}")

def update_skills_master_doc(skill_name, description):
    """Updates the Capabilities section in skills-master/SKILL.md"""
    if not os.path.exists(SKILLS_MASTER_DOC):
        print(f"Warning: Could not find {SKILLS_MASTER_DOC} to update.")
        return

    with open(SKILLS_MASTER_DOC, 'r') as f:
        content = f.read()

    # Look for the Capabilities list
    # It usually starts after "## Capabilities" and contains lines starting with "*   **"
    
    # We want to check if the skill is already listed
    pattern = re.compile(f"\\*\\s+\\*\\*{re.escape(skill_name)}\\*\\*:")
    
    new_entry = f"*   **{skill_name}**: {description}"
    
    if pattern.search(content):
        # Update existing entry
        # Replace the line containing the skill
        print(f"Updating existing entry for {skill_name} in skills-master/SKILL.md...")
        content = re.sub(f"\\*\\s+\\*\\*{re.escape(skill_name)}\\*\\*:.*", new_entry, content)
    else:
        # Add new entry
        # Find the end of the list (or the Capabilities section)
        print(f"Adding new entry for {skill_name} to skills-master/SKILL.md...")
        
        # Simple heuristic: find the last list item and append after it
        # Or look for "## Capabilities" and append to the list following it
        
        # Let's find the "## Capabilities" section
        # Look for the introductory line: "The following skill templates are available in `assets/skill-templates/`:"
        # Or just "## Capabilities"
        
        # Try to match the section header and the list following it
        # The list items usually start with "*   **"
        
        # More robust regex:
        # 1. Find "## Capabilities"
        # 2. Find the list block after it (possibly separated by text)
        
        capabilities_start = content.find("## Capabilities")
        if capabilities_start != -1:
             # Find the first list item after this section
             list_start_match = re.search(r"\n\*   \*\*", content[capabilities_start:])
             if list_start_match:
                 list_start_index = capabilities_start + list_start_match.start()
                 
                 # Now find the end of the list
                 # We assume the list ends when we hit a line that doesn't start with "*   " or empty line followed by new section
                 # But simplistic approach: just find the block of lines starting with "*   "
                 
                 # Let's grab the whole text after the first list item
                 rest_of_text = content[list_start_index:]
                 
                 # Split into lines
                 lines = rest_of_text.split('\n')
                 list_lines = []
                 post_list_lines = []
                 in_list = True
                 
                 for line in lines:
                     if in_list:
                         if line.strip() == "" or line.strip().startswith("*   "):
                             list_lines.append(line)
                         else:
                             in_list = False
                             post_list_lines.append(line)
                     else:
                         post_list_lines.append(line)
                 
                 # Filter only actual list items from list_lines (remove empty lines for sorting)
                 clean_list_items = [l for l in list_lines if l.strip().startswith("*   ")]
                 
                 # Add new item
                 clean_list_items.append(new_entry)
                 
                 # Sort
                 def get_name(line):
                     m = re.search(r"\*\*\s*(.+?)\s*\*\*", line)
                     return m.group(1) if m else ""
                 clean_list_items.sort(key=get_name)
                 
                 # Reconstruct
                 # We need to preserve the text before the list
                 pre_list_text = content[:list_start_index]
                 
                 # Join list items
                 new_list_text = "\n".join(clean_list_items)
                 
                 # Join post list text
                 post_list_text = "\n".join(post_list_lines)
                 
                 content = pre_list_text + "\n" + new_list_text + "\n" + post_list_text
             else:
                 # No list found in Capabilities, append to end of section
                 # Just insert after the header + some text
                 # Look for next header
                 next_header = re.search(r"\n## ", content[capabilities_start+1:])
                 if next_header:
                     insert_pos = capabilities_start + 1 + next_header.start()
                     content = content[:insert_pos] + "\n" + new_entry + "\n" + content[insert_pos:]
                 else:
                     # End of file
                     content += "\n" + new_entry + "\n"
        else:
             print("Warning: Could not locate '## Capabilities' section in SKILL.md")

    with open(SKILLS_MASTER_DOC, 'w') as f:
        f.write(content)
    print("Successfully updated skills-master/SKILL.md")

def create_skill_skeleton(name, description, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    
    # Create SKILL.md only if it doesn't exist (to preserve source content if partially copied)
    skill_md_path = os.path.join(target_dir, "SKILL.md")
    if not os.path.exists(skill_md_path):
        skill_md_content = f"""---
name: "{name}"
description: "{description}"
---

# {name.replace('-', ' ').title()}

{description}

## Usage

<!-- Add usage instructions here -->
"""
        with open(skill_md_path, "w") as f:
            f.write(skill_md_content)
        
    # Create scripts directory
    os.makedirs(os.path.join(target_dir, "scripts"), exist_ok=True)
    print(f"Created skeleton for '{name}' at {target_dir}")

def add_skill(name, description, source_path=None):
    target_dir = os.path.join(SKILLS_MASTER_TEMPLATES, name)
    
    if os.path.exists(target_dir):
        print(f"Warning: Skill template '{name}' already exists in skills-master. Updating...")
        # Don't delete self if updating self
        if os.path.abspath(target_dir) != os.path.dirname(os.path.dirname(os.path.abspath(__file__))):
            shutil.rmtree(target_dir)
        else:
            print("Self-update detected. Skipping deletion.")
    
    if source_path:
        # Resolve source path
        source_abs = os.path.abspath(source_path)
        if not os.path.exists(source_abs):
            print(f"Error: Source path '{source_path}' does not exist.")
            return False
        
        # Avoid copying self to self
        if source_abs == os.path.abspath(target_dir):
            print("Source and target are the same directory. Skipping copy.")
        else:
            print(f"Copying skill from '{source_abs}' to '{target_dir}'...")
            # shutil.copytree fails if dest exists, so we need to be careful
            if os.path.exists(target_dir):
                 try:
                    shutil.copytree(source_abs, target_dir, dirs_exist_ok=True)
                 except shutil.Error as e:
                    # Ignore "are the same file" errors if we missed the dir check
                    print(f"Copy warning: {e}")
            else:
                 shutil.copytree(source_abs, target_dir)
        
        # Verify SKILL.md exists
        if not os.path.exists(os.path.join(target_dir, "SKILL.md")):
            print(f"Warning: Source skill does not contain SKILL.md. Creating a default one.")
            create_skill_skeleton(name, description, target_dir)
            
    else:
        create_skill_skeleton(name, description, target_dir)
        
    print(f"Successfully added '{name}' to skills-master templates.")
    
    # Update skills-master/SKILL.md
    update_skills_master_doc(name, description)
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a skill to skills-master templates.")
    parser.add_argument("--name", required=True, help="Name of the skill")
    parser.add_argument("--description", required=True, help="Description of the skill")
    parser.add_argument("--source", help="Path to existing skill directory to copy")
    
    args = parser.parse_args()
    
    print(f"DEBUG: calling add_skill with name={args.name}", flush=True)
    if not os.path.exists(SKILLS_MASTER_TEMPLATES):
        print(f"Error: skills-master templates directory not found at {SKILLS_MASTER_TEMPLATES}", flush=True)
        print("Make sure skills-master is installed correctly.", flush=True)
        sys.exit(1)
        
    add_skill(args.name, args.description, args.source)
