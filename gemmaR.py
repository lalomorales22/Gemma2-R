# Filename: gemmaR.py

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import requests
import json
import logging
import re
import configparser
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Gemma2ChatApp:
    def __init__(self, master):
        self.master = master
        master.title("Gemma 2 Advanced Software Engineering Chat")
        master.geometry("1200x900")
        
        self.style = ttk.Style()
        self.config = self.load_config()
        self.setup_gui()  # Move this before setup_styles
        self.setup_styles()
        
        self.ollama_url = self.config.get('API', 'ollama_url')
        self.system_prompt = self.load_system_prompt()
        self.conversation_history = []
        self.add_message("Gemma 2 Advanced Software Engineering Chat initialized. Let's engineer robust solutions!")

    def load_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if 'API' not in config:
            config['API'] = {'ollama_url': 'http://localhost:11434/api/generate'}
        if 'GUI' not in config:
            config['GUI'] = {'theme': 'clam', 'font_size': '10'}
        return config

    def setup_gui(self):
        self.create_menu()
        self.create_chat_area()
        self.create_input_area()
        self.create_control_buttons()

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Chat Log", command=self.save_chat_log)
        file_menu.add_command(label="Exit", command=self.master.quit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Chat", command=self.clear_chat)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Increase Font Size", command=lambda: self.change_font_size(1))
        view_menu.add_command(label="Decrease Font Size", command=lambda: self.change_font_size(-1))
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)

    def create_chat_area(self):
        self.chat_frame = ttk.Frame(self.master, padding="10")
        self.chat_frame.pack(expand=True, fill='both')

        self.chat_log = scrolledtext.ScrolledText(self.chat_frame, state='disabled', wrap=tk.WORD, font=("Arial", int(self.config.get('GUI', 'font_size'))))
        self.chat_log.pack(expand=True, fill='both')

    def create_input_area(self):
        self.input_frame = ttk.Frame(self.master, padding="10")
        self.input_frame.pack(fill='x')

        self.input_field = ttk.Entry(self.input_frame, font=("Arial", int(self.config.get('GUI', 'font_size'))))
        self.input_field.pack(side='left', expand=True, fill='x')
        self.input_field.bind("<Return>", self.send_message)

        self.send_button = ttk.Button(self.input_frame, text='Send', command=self.send_message)
        self.send_button.pack(side='right', padx=(10, 0))

    def create_control_buttons(self):
        self.control_frame = ttk.Frame(self.master, padding="10")
        self.control_frame.pack(fill='x')

        self.clear_button = ttk.Button(self.control_frame, text='Clear Chat', command=self.clear_chat)
        self.clear_button.pack(side='left', padx=5)

        self.theme_button = ttk.Button(self.control_frame, text='Toggle Theme', command=self.toggle_theme)
        self.theme_button.pack(side='left', padx=5)

    def setup_styles(self):
        available_themes = self.style.theme_names()
        config_theme = self.config.get('GUI', 'theme')
        
        if config_theme in available_themes:
            self.style.theme_use(config_theme)
        else:
            # Fallback to a default theme
            fallback_theme = 'clam' if 'clam' in available_themes else available_themes[0]
            self.style.theme_use(fallback_theme)
            self.config.set('GUI', 'theme', fallback_theme)
            logger.warning(f"Theme '{config_theme}' not found. Using '{fallback_theme}' instead.")
        
        self.update_styles()

    def update_styles(self):
        current_theme = self.style.theme_use()
        bg_color = self.style.lookup('TFrame', 'background') or "#ffffff"
        fg_color = self.style.lookup('TLabel', 'foreground') or "#000000"
        
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TButton", padding=6, relief="flat")
        self.style.configure("TEntry", padding=6, relief="flat")
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        
        # Check if chat_log exists before configuring it
        if hasattr(self, 'chat_log'):
            self.chat_log.config(bg=bg_color, fg=fg_color)
        
        self.master.configure(bg=bg_color)

    def toggle_theme(self):
        available_themes = self.style.theme_names()
        current_theme = self.style.theme_use()
        
        # Simple toggle between two themes, adjust as needed
        new_theme = 'clam' if current_theme != 'clam' else 'alt'
        
        if new_theme in available_themes:
            self.style.theme_use(new_theme)
            self.config.set('GUI', 'theme', new_theme)
            self.update_styles()
            self.save_config()
        else:
            logger.warning(f"Theme '{new_theme}' not available. Keeping current theme.")

    def change_font_size(self, delta):
        current_size = int(self.config.get('GUI', 'font_size'))
        new_size = max(8, min(current_size + delta, 20))
        self.config.set('GUI', 'font_size', str(new_size))
        self.chat_log.config(font=("Arial", new_size))
        self.input_field.config(font=("Arial", new_size))
        self.save_config()

    def save_config(self):
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def load_system_prompt(self):
        prompt = """You are Gemma 2, an advanced AI assistant created by Google, specializing in software engineering with enhanced reasoning capabilities. Your responses should demonstrate depth, clarity, and technical precision while maintaining an approachable tone. Always provide complete, production-ready file implementations.

Follow this structured approach in your reasoning and response formulation:

1. Problem Analysis:
   a) Identify key concepts, technologies, and potential challenges.
   b) Activate relevant knowledge bases from software engineering domains.

2. Design Consideration:
   a) Consider appropriate design patterns and architectural styles.
   b) Evaluate trade-offs between different approaches.

3. Implementation Planning:
   a) Break down the problem into manageable components.
   b) Outline a high-level implementation strategy.

4. Code Development:
   a) Write clean, efficient, and well-documented code.
   b) Implement robust error handling and follow best practices.

5. Testing and Quality Assurance:
   a) Suggest unit tests and integration tests.
   b) Consider edge cases and potential failure modes.

6. Performance and Scalability:
   a) Analyze time and space complexity.
   b) Suggest optimizations and scalability improvements.

7. Security Considerations:
   a) Identify potential security vulnerabilities.
   b) Recommend secure coding practices.

8. Deployment and DevOps:
   a) Discuss deployment strategies and potential challenges.
   b) Consider containerization, CI/CD pipelines, and monitoring.

9. Maintenance and Future-Proofing:
   a) Discuss strategies for long-term maintenance.
   b) Consider extensibility and potential future enhancements.

10. Code Review and Best Practices:
    a) Provide a self-review of the implemented solution.
    b) Highlight adherence to coding standards and best practices.

For each response:
1. Begin with a concise summary of your approach and main conclusions.
2. Present your detailed chain of thought, explaining key decisions.
3. Provide the complete code implementation with appropriate markdown.
4. Address limitations and suggest areas for improvement.
5. Propose testing strategies and deployment considerations.

Use the following tags to structure your response:
<thinking> for your initial chain of thought
<analyzing> for critical evaluation and refinement
<implementing> for the actual code development process

Maintain a balance between technical depth and clarity, promoting best practices and robust design principles throughout your response."""
        return prompt

    def send_message(self, event=None):
        message = self.input_field.get().strip()
        if message:
            self.add_message(f"You: {message}", tag="user")
            self.input_field.delete(0, 'end')
            threading.Thread(target=self.process_and_send_to_ollama, args=(message,)).start()

    def process_and_send_to_ollama(self, message):
        try:
            if not self.conversation_history:
                self.conversation_history = [{"role": "system", "content": self.system_prompt}]
            
            self.conversation_history.append({"role": "user", "content": message})
            
            prompt = f"Human: {message}\nAssistant: Initiating comprehensive software engineering analysis and implementation.\n"
            self.stream_response(prompt)

        except Exception as e:
            logger.error(f"Error in processing message: {str(e)}", exc_info=True)
            self.add_message(f"An error occurred: {str(e)}", tag="error")

    def stream_response(self, prompt):
        payload = {
            "model": "gemma2:2b",
            "prompt": self.format_conversation() + prompt,
            "stream": True
        }
        try:
            response = requests.post(self.ollama_url, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            
            full_response = ""
            current_section = None
            section_content = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get('response', '')
                    full_response += chunk
                    
                    if "<thinking>" in chunk:
                        current_section = "thinking"
                        self.start_section_display("Thought Process")
                    elif "<analyzing>" in chunk:
                        if current_section:
                            self.end_section_display(current_section, section_content)
                        current_section = "analyzing"
                        section_content = ""
                        self.start_section_display("Critical Analysis")
                    elif "<implementing>" in chunk:
                        if current_section:
                            self.end_section_display(current_section, section_content)
                        current_section = "implementing"
                        section_content = ""
                        self.start_section_display("Implementation")
                    elif "</thinking>" in chunk or "</analyzing>" in chunk or "</implementing>" in chunk:
                        if current_section:
                            self.end_section_display(current_section, section_content)
                        current_section = None
                        section_content = ""
                    
                    if current_section:
                        section_content += chunk
                        self.update_section_content(chunk)
                    else:
                        self.update_chat_log(chunk)
                    
                    self.check_and_display_code(chunk)
                    
                    if data.get('done', False):
                        break
            
            if full_response:
                self.conversation_history.append({"role": "assistant", "content": full_response})
            else:
                logger.warning("Empty response received from Ollama")
                self.add_message("Gemma 2: (No response received. The model might be processing or there might be an issue.)", tag="error")

        except requests.RequestException as e:
            logger.error(f"Error in API request: {str(e)}", exc_info=True)
            self.add_message(f"Error in communication with Ollama: {str(e)}", tag="error")

    def check_and_display_code(self, chunk):
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', chunk, re.DOTALL)
        for language, code in code_blocks:
            filename = self.extract_filename(code)
            self.display_code_window(language, code, filename)

    def extract_filename(self, code):
        filename_match = re.search(r'# Filename: (.+)', code)
        return filename_match.group(1) if filename_match else "Untitled"

    def display_code_window(self, language, code, filename):
        code_window = tk.Toplevel(self.master)
        code_window.title(f"Code Implementation - {filename}")
        code_window.geometry("800x600")

        code_frame = ttk.Frame(code_window, padding="10")
        code_frame.pack(expand=True, fill='both')

        code_display = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD, font=("Courier", int(self.config.get('GUI', 'font_size'))))
        code_display.pack(expand=True, fill='both')
        code_display.insert(tk.END, code)
        code_display.config(state='disabled')

        button_frame = ttk.Frame(code_window)
        button_frame.pack(fill='x', pady=10)

        copy_button = ttk.Button(button_frame, text="Copy Code", command=lambda: self.copy_to_clipboard(code))
        copy_button.pack(side='left', padx=5)

        save_button = ttk.Button(button_frame, text="Save to File", command=lambda: self.save_to_file(filename, code))
        save_button.pack(side='left', padx=5)

    def copy_to_clipboard(self, text):
        self.master.clipboard_clear()
        self.master.clipboard_append(text)
        self.master.update()
        messagebox.showinfo("Copied", "Code copied to clipboard!")

    def save_to_file(self, filename, code):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", initialfile=filename)
        if file_path:
            with open(file_path, 'w') as file:
                file.write(code)
            messagebox.showinfo("Saved", f"Code saved to {file_path}")

    def start_section_display(self, title):
        self.section_frame = ttk.Frame(self.chat_frame, relief="raised", borderwidth=1)
        self.section_frame.pack(fill='x', padx=5, pady=5)
        
        self.section_label = ttk.Label(self.section_frame, text=title, font=("Arial", int(self.config.get('GUI', 'font_size')), "bold"))
        self.section_label.pack(anchor='w', padx=5, pady=5)
        
        self.section_content = scrolledtext.ScrolledText(self.section_frame, wrap=tk.WORD, height=6, font=("Arial", int(self.config.get('GUI', 'font_size'))-1))
        self.section_content.pack(fill='both', expand=True, padx=5, pady=5)

    def update_section_content(self, chunk):
        self.master.after(0, self._update_section_content, chunk)

    def _update_section_content(self, chunk):
        self.section_content.config(state='normal')
        self.section_content.insert('end', chunk)
        self.section_content.config(state='disabled')
        self.section_content.see('end')

    def end_section_display(self, section_type, content):
        self.section_frame.destroy()
        self.add_message(f"{section_type.capitalize()}:\n{content}", tag=section_type)

    def update_chat_log(self, chunk):
        self.master.after(0, self._update_chat_log, chunk)

    def _update_chat_log(self, chunk):
        self.chat_log.config(state='normal')
        self.chat_log.insert('end', chunk, "assistant")
        self.chat_log.config(state='disabled')
        self.chat_log.see('end')

    def format_conversation(self):
        formatted = ""
        for message in self.conversation_history:
            if message["role"] == "system":
                formatted += f"System: {message['content']}\n"
            elif message["role"] == "user":
                formatted += f"Human: {message['content']}\n"
            elif message["role"] == "assistant":
                formatted += f"Assistant: {message['content']}\n"
        return formatted.strip()

    def add_message(self, message, tag=None):
        self.chat_log.config(state='normal')
        self.chat_log.insert('end', message + '\n\n', tag)
        self.chat_log.config(state='disabled')
        self.chat_log.see('end')
        logger.debug(f"Added message to chat log: {message}")

        # Configure tags for different message types
        self.chat_log.tag_configure("user", foreground="blue")
        self.chat_log.tag_configure("assistant", foreground="green")
        self.chat_log.tag_configure("error", foreground="red")
        self.chat_log.tag_configure("thinking", foreground="purple")
        self.chat_log.tag_configure("analyzing", foreground="orange")
        self.chat_log.tag_configure("implementing", foreground="brown")

    def clear_chat(self):
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.chat_log.config(state='normal')
            self.chat_log.delete(1.0, 'end')
            self.chat_log.config(state='disabled')
            self.conversation_history = []
            self.add_message("Chat cleared. Ready for a new software engineering discourse!")

    def save_chat_log(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.chat_log.get(1.0, tk.END))
            messagebox.showinfo("Saved", f"Chat log saved to {file_path}")

def main():
    root = tk.Tk()
    app = Gemma2ChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()