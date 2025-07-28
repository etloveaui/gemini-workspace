import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

def main():
    section_arg = "all"
    if len(sys.argv) > 1:
        section_arg = sys.argv[1]

    help_file_path = os.path.join(os.path.dirname(__file__), "..", "docs", "HELP.md")

    try:
        with open(help_file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: HELP.md not found at {help_file_path}")
        sys.exit(1)

    if section_arg == "all":
        print(content)
    else:
        # Split content by "## " to get sections. The first element will be content before the first section.
        sections = content.split("## ")
        found_section_content = None
        available_sections = []

        # Iterate from the second element, as the first element is content before any section.
        for s_block in sections[1:]:
            # The first line of each block is the section title
            lines = s_block.splitlines()
            if not lines:
                continue
            current_section_title = lines[0].strip()
            available_sections.append(current_section_title)

            # Check if the current section title matches the requested section_arg
            if current_section_title.lower() == section_arg.lower():
                # Reconstruct the section content including its title
                found_section_content = "## " + s_block
                break

        if found_section_content:
            print(found_section_content)
        else:
            print(f"Error: Section '{section_arg}' not found.")
            print("Available sections (case-insensitive):")
            for sec_title in available_sections:
                print(f"- {sec_title}")

    sys.exit(0)

if __name__ == "__main__":
    main()