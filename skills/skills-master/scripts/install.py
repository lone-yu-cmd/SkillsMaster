import os
import shutil
import argparse
import sys

# Constants
SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "skill-templates")

def install_skill(skill_name):
    src = os.path.join(TEMPLATES_DIR, skill_name)
    dst = os.path.join(SKILLS_DIR, skill_name)
    
    if not os.path.exists(src):
        print(f"Error: Skill template '{skill_name}' not found.")
        return False
        
    if os.path.exists(dst):
        print(f"Warning: Skill '{skill_name}' already exists. Skipping.")
        return False
        
    shutil.copytree(src, dst)
    print(f"Successfully installed skill: {skill_name}")
    return True

def list_templates():
    if not os.path.exists(TEMPLATES_DIR):
        print("No templates found.")
        return []
    return [d for d in os.listdir(TEMPLATES_DIR) if os.path.isdir(os.path.join(TEMPLATES_DIR, d))]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install standard skills from templates.")
    parser.add_argument("--name", help="Name of the skill to install")
    parser.add_argument("--all", action="store_true", help="Install all available skills")
    parser.add_argument("--list", action="store_true", help="List available templates")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available Skill Templates:")
        for t in list_templates():
            print(f"- {t}")
        sys.exit(0)
        
    if args.all:
        for t in list_templates():
            install_skill(t)
    elif args.name:
        install_skill(args.name)
    else:
        parser.print_help()
