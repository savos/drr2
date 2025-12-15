#!/bin/bash
# Script to add or remove .claude and root .md files from .gitignore

GITIGNORE_FILE=".gitignore"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define the entries to manage
ENTRIES=(
    "# Claude Code configuration"
    ".claude/"
    ""
    "# Documentation files - all root markdown files"
    "AGENTS.md"
    "CLAUDE.md"
    "AUTOMATIC-MIGRATIONS-SETUP.md"
    "README.md"
    "GETTING-STARTED.md"
    "PROJECT-OVERVIEW.md"
)

# Function to check if entry exists in .gitignore
entry_exists() {
    local entry="$1"
    if [ ! -f "$GITIGNORE_FILE" ]; then
        return 1
    fi
    # Handle both Unix (LF) and Windows (CRLF) line endings
    grep -qF "$entry" "$GITIGNORE_FILE" 2>/dev/null
    return $?
}

# Function to add entries to .gitignore
add_entries() {
    echo "Adding .claude and root .md files to .gitignore..."

    if [ ! -f "$GITIGNORE_FILE" ]; then
        echo "Creating .gitignore file..."
        touch "$GITIGNORE_FILE"
    fi

    # Check if any of our entries already exist
    local already_exists=false
    for entry in "${ENTRIES[@]}"; do
        if [ -n "$entry" ] && ! [[ "$entry" =~ ^# ]]; then
            if entry_exists "$entry"; then
                already_exists=true
                break
            fi
        fi
    done

    if [ "$already_exists" = true ]; then
        echo "⚠️  Some entries already exist in .gitignore"
        read -p "Do you want to continue? This may create duplicates. (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted."
            exit 1
        fi
    fi

    # Add entries to .gitignore
    echo "" >> "$GITIGNORE_FILE"
    for entry in "${ENTRIES[@]}"; do
        echo "$entry" >> "$GITIGNORE_FILE"
    done

    echo "✓ Successfully added entries to .gitignore"
    echo ""
    echo "Added entries:"
    printf '%s\n' "${ENTRIES[@]}" | grep -v "^#" | grep -v "^$"
}

# Function to remove entries from .gitignore
remove_entries() {
    echo "Removing .claude and root .md files from .gitignore..."

    if [ ! -f "$GITIGNORE_FILE" ]; then
        echo "✓ .gitignore file does not exist. Nothing to remove."
        exit 0
    fi

    # Create temporary file
    local temp_file=$(mktemp)

    # Track removed lines
    local removed_count=0
    local in_our_section=false

    while IFS= read -r line || [ -n "$line" ]; do
        # Remove any trailing carriage return (Windows line endings)
        line="${line%$'\r'}"

        # Check if this is the start of our section
        if [ "$line" = "# Claude Code configuration" ]; then
            in_our_section=true
            continue
        fi

        # Check if this is the documentation section comment
        if [ "$line" = "# Documentation files - all root markdown files" ]; then
            in_our_section=true
            continue
        fi

        # Check if we should skip this line (it's one of our entries)
        local skip=false
        for entry in "${ENTRIES[@]}"; do
            # Skip empty lines and comments in ENTRIES array
            if [ -z "$entry" ] || [[ "$entry" =~ ^# ]]; then
                continue
            fi

            if [ "$line" = "$entry" ]; then
                skip=true
                removed_count=$((removed_count + 1))
                break
            fi
        done

        # If we're in our section and hit an empty line, skip it
        if [ "$in_our_section" = true ] && [ -z "$line" ]; then
            skip=true
        fi

        # If we're in our section and hit a non-empty line that's not ours, we're out
        if [ "$in_our_section" = true ] && [ -n "$line" ] && [ "$skip" = false ] && ! [[ "$line" =~ ^# ]]; then
            in_our_section=false
        fi

        # Write line if we're not skipping it
        if [ "$skip" = false ]; then
            echo "$line" >> "$temp_file"
        fi
    done < "$GITIGNORE_FILE"

    # Replace original file with cleaned version
    mv "$temp_file" "$GITIGNORE_FILE"

    if [ $removed_count -gt 0 ]; then
        echo "✓ Successfully removed $removed_count entries from .gitignore"
    else
        echo "✓ No matching entries found in .gitignore"
    fi
}

# Function to show current status
show_status() {
    echo "Checking .gitignore status..."
    echo ""

    if [ ! -f "$GITIGNORE_FILE" ]; then
        echo "⚠️  .gitignore file does not exist"
        exit 0
    fi

    echo "Entries status:"
    echo "------------------------"

    local found_count=0
    for entry in "${ENTRIES[@]}"; do
        if [ -n "$entry" ] && ! [[ "$entry" =~ ^# ]] && [ "$entry" != "" ]; then
            if entry_exists "$entry"; then
                echo "✓ $entry (in .gitignore)"
                found_count=$((found_count + 1))
            else
                echo "✗ $entry (not in .gitignore)"
            fi
        fi
    done

    echo "------------------------"
    echo "Total: $found_count entries in .gitignore"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTION]

Options:
  -add       Add .claude and root .md files to .gitignore
  -remove    Remove .claude and root .md files from .gitignore
  -status    Show current status of entries in .gitignore
  -help      Show this help message

Examples:
  $0 -add       # Add entries to .gitignore
  $0 -remove    # Remove entries from .gitignore
  $0 -status    # Check current status

Managed entries:
  - .claude/ directory
  - Root markdown files: AGENTS.md, CLAUDE.md, AUTOMATIC-MIGRATIONS-SETUP.md,
    README.md, GETTING-STARTED.md, PROJECT-OVERVIEW.md

EOF
}

# Main script logic
main() {
    # Change to script directory
    cd "$SCRIPT_DIR" || exit 1

    case "${1:-}" in
        -add)
            add_entries
            ;;
        -remove)
            remove_entries
            ;;
        -status)
            show_status
            ;;
        -help|--help|-h)
            show_usage
            ;;
        *)
            echo "Error: Invalid option '${1:-}'"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
