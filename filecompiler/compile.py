import os
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from pathlib import Path
import magic  
DEFAULT_EXCLUDE = {
    'dirs': {'dist', '.git', 'venv', 'node_modules', '__pycache__'},  
    'extensions': {'.pyc', '.json'}  }

def detect_language(file_path, content):
    """Detect programming language based on file extension and content."""
    extension = Path(file_path).suffix.lower()
    
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript/React',
        '.java': 'Java',
        '.html': 'HTML',
        '.css': 'CSS',
        '.xml': 'XML',
    }
    
    return language_map.get(extension, 'Unknown')

def should_skip_path(path, exclude_patterns=None):
    """Check if a path should be skipped based on exclusion patterns."""
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE
        
    path_obj = Path(path)
    
    print(f"Checking path: {path}")
    print(f"Extension: {path_obj.suffix}")
    
    for parent in path_obj.parents:
        if parent.name in exclude_patterns['dirs']:
            print(f"Skipping due to excluded directory: {parent.name}")
            return True
            
    if path_obj.suffix.lower() in exclude_patterns['extensions']:
        print(f"Skipping due to excluded extension: {path_obj.suffix}")
        return True
        
    return False

def analyze_code_files(directory_path, exclude_patterns=None):
    """Analyze code files in a directory and return a dictionary with their contents and metadata."""
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE
        
    analysis_data = {
        'directory': os.path.abspath(directory_path),
        'files': [],
        'errors': []
    }
    
    print(f"\nStarting analysis of directory: {directory_path}")
    
    for root_dir, dirs, files in os.walk(directory_path):
        print(f"\nExamining directory: {root_dir}")
        print(f"Found files: {files}")
        
        for file_name in files:
            file_path = os.path.join(root_dir, file_name)
            print(f"\nProcessing file: {file_path}")
            
            if should_skip_path(file_path, exclude_patterns):
                continue
                
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 10 * 1024 * 1024:  # 10MB
                    print(f"Skipping large file: {file_path} ({file_size} bytes)")
                    continue
                
                mime = magic.Magic(mime=True)
                file_type = mime.from_file(file_path)
                print(f"File MIME type: {file_type}")
                
                if not (file_type.startswith('text/') or 
                       file_type == 'application/javascript' or
                       file_type == 'application/json' or
                       file_type == 'application/xml'):
                    print(f"Skipping non-text file: {file_path} ({file_type})")
                    continue
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_data = {
                    'path': os.path.relpath(file_path, directory_path),
                    'name': file_name,
                    'size': os.path.getsize(file_path),
                    'language': detect_language(file_path, content),
                    'last_modified': os.path.getmtime(file_path),
                    'content': content,
                    'statistics': {
                        'lines': len(content.splitlines()),
                        'characters': len(content)
                    }
                }
                
                print(f"Successfully processed: {file_path}")
                analysis_data['files'].append(file_data)
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                error_data = {
                    'file': file_path,
                    'message': str(e)
                }
                analysis_data['errors'].append(error_data)
    
    return analysis_data

def save_output(analysis_data, output_file='code_analysis.json', format='json'):
    """Save the analysis data to a file in the specified format."""
    print(f"\nSaving output to: {output_file}")
    if format == 'json':
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=4)
            print(f"Successfully saved JSON output")
    else:
        raise ValueError(f"Unsupported output format: {format}")

def main():
    """Main function to run the code analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze code files and create output file')
    parser.add_argument('directory', help='Directory path containing code files')
    parser.add_argument('--output', default='code_analysis.json', help='Output file name')
    
    args = parser.parse_args()
    
    print(f"Starting analysis with minimal exclusions")
    analysis_data = analyze_code_files(args.directory, DEFAULT_EXCLUDE)
    save_output(analysis_data, args.output)
    print(f"Analysis complete. Found {len(analysis_data['files'])} files.")
    print(f"Output written to: {args.output}")

if __name__ == '__main__':
    main()
