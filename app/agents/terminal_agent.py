import os
import re
import platform
import logging
from typing import List, Optional, Set, Dict, Any, Tuple
from dataclasses import dataclass, field
from .prompts.terminal_prompt import TERMINAL_PROMPT

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class AgentContext:
    """
    Handles system and environment context for command execution.
    Supports rich context for environment-aware command generation.
    """
    data: Dict[str, Any] = field(default_factory=dict)
    
    # ===== Basic System Context =====
    @property
    def os_kind(self) -> str:
        return self.data.get("os") or self.data.get("os_kind") or platform.system()
    
    @property
    def cwd(self) -> str:
        return self.data.get("current_directory") or self.data.get("cwd") or os.getcwd()
    
    # ===== Execution Environment Context =====
    @property
    def execution(self) -> str:
        """Execution mode: local, remote, docker, container, cloud"""
        return self.data.get("execution", "local")
    
    @property
    def host(self) -> Optional[str]:
        """Remote host for SSH execution"""
        return self.data.get("host")
    
    @property
    def user(self) -> Optional[str]:
        """Remote user for SSH execution"""
        return self.data.get("user")
    
    @property
    def container(self) -> Optional[str]:
        """Docker container name"""
        return self.data.get("container")
    
    @property
    def port(self) -> Optional[int]:
        """Remote port for SSH"""
        return self.data.get("port", 22)
    
    # ===== Runtime Context =====
    @property
    def venv(self) -> Optional[str]:
        """Virtual environment path"""
        return self.data.get("venv")
    
    @property
    def language(self) -> Optional[str]:
        """Programming language context"""
        return self.data.get("language")
    
    @property
    def framework(self) -> Optional[str]:
        """Framework context (django, flask, express, etc.)"""
        return self.data.get("framework")
    
    @property
    def shell(self) -> str:
        """Shell type (bash, zsh, powershell, cmd)"""
        return self.data.get("shell", "bash" if self.os_kind != "Windows" else "powershell")
    
    # ===== Security Context =====
    @property
    def security_policy(self) -> str:
        """Security policy: standard, restricted"""
        return self.data.get("security_policy", "standard")
    
    # ===== Cloud Context =====
    @property
    def cloud_provider(self) -> Optional[str]:
        """Cloud provider: aws, gcp, azure"""
        return self.data.get("cloud_provider")
    
    @property
    def cloud_profile(self) -> Optional[str]:
        """Cloud profile/credentials"""
        return self.data.get("cloud_profile")
    
    @property
    def cloud_region(self) -> Optional[str]:
        """Cloud region"""
        return self.data.get("cloud_region")
    
    # ===== Database Context =====
    @property
    def database(self) -> Optional[str]:
        """Database name"""
        return self.data.get("database")
    
    @property
    def db_user(self) -> Optional[str]:
        """Database user"""
        return self.data.get("db_user")
    
    @property
    def db_type(self) -> Optional[str]:
        """Database type: postgres, mysql, mongodb"""
        return self.data.get("db_type")
    
    @property
    def db_host(self) -> Optional[str]:
        """Database host"""
        return self.data.get("db_host", "localhost")

class SafetyValidator:
    """
    Enterprise-grade security layer for terminal command validation.
    Implements allowlist, blacklist, and character-level sanitization.
    """
    def __init__(self, context: AgentContext):
        self.context = context
        self.allowlist: Set[str] = {
            "ls", "pwd", "echo", "cat", "grep", "find", 
            "head", "tail", "wc", "mkdir", "touch", "cp", "mv",
            "dir", "cd", "type", "findstr"
        }
        
        self.blacklist_patterns: List[str] = [
            r"rm\s+-rf", r"shutdown", r"reboot", r"mkfs", r"dd",
            r":\(\)\{\s+:\|:&\s+\};:", r"sudo", r"chmod\s+777",
            r"chown", r"systemctl", r"service", r"history\s+-c"
        ]
        
        self.blocked_meta_chars: Set[str] = {";", "&", "|", "`", "$", "(", ")", ">", "<", "*", "?", "[", "]", "{", "}"}
        self.restricted_paths: List[str] = ["/etc", "/bin", "/usr", "/root", "/boot", "/proc", "/sys", "/dev"]

    def is_safe(self, command_str: str) -> bool:
        """Performs multi-layered safety checks on the generated command."""
        if not command_str or not isinstance(command_str, str):
            return False
            
        cmd = command_str.strip()
        
        # 1. Block Meta-characters (Chaining, Redirection, Expansion, Globbing)
        if any(char in cmd for char in self.blocked_meta_chars):
            return False

        # 2. Block Blacklisted Destructive Patterns
        for pattern in self.blacklist_patterns:
            if re.search(pattern, cmd, re.IGNORECASE):
                return False

        # 3. Path Validation and Restriction
        tokens = cmd.split()
        if not tokens:
            return False
            
        for token in tokens:
            if ".." in token:
                return False
            
            # Normalize and check restricted system paths
            norm_token = token.replace("\\", "/")
            if norm_token.startswith("/") or re.match(r"^[a-zA-Z]:", norm_token):
                for restricted in self.restricted_paths:
                    if norm_token == restricted or norm_token.startswith(restricted + "/"):
                        return False

        # 4. Command Allowlist Enforcement
        base_cmd = tokens[0]
        if base_cmd not in self.allowlist:
            return False

        # 5. Logic-specific constraints
        if base_cmd == "cp" and ("-r" in tokens or "-R" in tokens):
            return False

        return True

class ExecutionPlanner:
    """
    Context-Driven Execution Planner.
    Converts (Query + Context) → Safe, Correct, Environment-Aware Command.
    
    Priority Resolution Order (Highest → Lowest):
    1. Security constraints
    2. Execution environment (remote, docker, container, cloud)
    3. Runtime context (venv, shell, OS)
    4. Language/toolchain context
    5. Project/build/test system
    6. General OS defaults
    """
    def __init__(self, context: AgentContext):
        self.context = context
        
    def plan(self, query: str) -> Dict[str, Any]:
        """
        Main planning logic. Returns execution plan with command, confidence, and explanation.
        """
        q = query.lower().strip()
        is_windows = self.context.os_kind.lower() == "windows"
        
        # Detect code generation requests
        code_keywords = ["write code", "create script", "generate function", "write a program", 
                        "code for", "script for", "function to", "program that"]
        if any(keyword in q for keyword in code_keywords):
            return {
                "base_command": "",
                "intent": "CODE_REQUEST",
                "confidence": 1.0
            }
        
        # Generate base command from query
        base_cmd = self._generate_base_command(q, is_windows)
        
        if base_cmd == "NEEDS_CLARIFICATION":
            return {
                "base_command": "",
                "intent": "NEEDS_CLARIFICATION",
                "confidence": 0.0
            }
        
        # Calculate confidence based on context completeness
        confidence = self._calculate_confidence(base_cmd)
        
        return {
            "base_command": base_cmd,
            "intent": "EXECUTE",
            "confidence": confidence
        }
    
    def _generate_base_command(self, q: str, is_windows: bool) -> str:
        """Generate base command from query using pattern matching."""
        
        # Framework-specific commands
        if self.context.framework == "django":
            if "migrate" in q or "migration" in q:
                return "python manage.py migrate"
            elif "run server" in q or "start server" in q:
                return "python manage.py runserver"
            elif "create app" in q:
                app_name = self._extract_subject(q, "app")
                return f"python manage.py startapp {app_name}" if app_name else "python manage.py startapp myapp"
        
        # Database commands
        if self.context.db_type == "postgres" and ("query" in q or "select" in q):
            return "SELECT_QUERY"  # Special marker for database execution
        
        # Standard file/directory operations
        if "list" in q and ("file" in q or "content" in q):
            return "dir" if is_windows else "ls -la"
        elif any(x in q for x in ["where am i", "current directory", "working directory"]):
            return "cd" if is_windows else "pwd"
        elif "create" in q and "directory" in q:
            name = self._extract_subject(q, "directory")
            return f"mkdir {name}" if name else "mkdir new_folder"
        elif "create" in q and "file" in q:
            name = self._extract_subject(q, "file")
            if is_windows:
                return f"type nul > {name}" if name else "type nul > new_file.txt"
            return f"touch {name}" if name else "touch new_file.txt"
        elif any(x in q for x in ["read", "show", "view"]):
            name = self._extract_raw_path(q)
            cmd = "type" if is_windows else "cat"
            return f"{cmd} {name}" if name else f"{cmd} document.txt"
        elif "count lines" in q:
            name = self._extract_raw_path(q)
            if is_windows:
                return f"find /c /v \"\" {name}" if name else "find /c /v \"\" data.log"
            return f"wc -l {name}" if name else "wc -l data.log"
        elif "search" in q or "find text" in q:
            term_match = re.search(r"'(.*?)'|\"(.*?)\"", q)
            term = term_match.group(1) or term_match.group(2) if term_match else "pattern"
            path = self._extract_raw_path(q) or "."
            if is_windows:
                return f"findstr /s /i {term} {path}"
            return f"grep -r {term} {path}"
        
        # Python-specific
        if self.context.language == "python":
            if "install" in q and "package" in q:
                pkg = self._extract_subject(q, "package")
                return f"pip install {pkg}" if pkg else "pip install <package>"
            elif "run" in q and "test" in q:
                return "pytest"
        
        if q.startswith("run:"):
            # This assumes 'query' is available, but it's 'q' here.
            # The original CommandParser had 'query' as a parameter to generate.
            # Let's assume the user_query from TerminalCommandAgent is passed here.
            # For now, I'll use 'q' and strip 'run:'
            return q.replace("run:", "", 1).strip()
            
        return "NEEDS_CLARIFICATION"
    
    def wrap_for_environment(self, base_cmd: str) -> str:
        """
        Wrap base command for execution environment.
        Implements priority-based conflict resolution.
        """
        cmd = base_cmd
        
        # Priority 1: Security constraints
        if self.context.security_policy == "restricted":
            # Check if command requires privileges
            restricted_commands = ["install", "apt", "yum", "dnf", "sudo", "chmod", "chown"]
            if any(rc in cmd.lower() for rc in restricted_commands):
                return "SECURITY_REFUSED"
        
        # Priority 2: Execution environment
        execution = self.context.execution
        
        if execution == "remote" and self.context.host:
            # SSH execution
            user = self.context.user or "root"
            host = self.context.host
            port = self.context.port
            if port != 22:
                cmd = f"ssh -p {port} {user}@{host} '{cmd}'"
            else:
                cmd = f"ssh {user}@{host} '{cmd}'"
            return cmd
        
        elif execution == "docker" and self.context.container:
            # Docker execution
            container = self.context.container
            cmd = f"docker exec {container} {cmd}"
            return cmd
        
        elif execution == "cloud":
            # Cloud execution (AWS example)
            if self.context.cloud_provider == "aws":
                profile = f"--profile {self.context.cloud_profile}" if self.context.cloud_profile else ""
                region = f"--region {self.context.cloud_region}" if self.context.cloud_region else ""
                # This is a simplified example - real AWS commands would be more complex
                cmd = f"aws {cmd} {profile} {region}".strip()
                return cmd
        
        # Priority 3: Runtime context
        if self.context.venv:
            # Virtual environment activation
            venv_path = self.context.venv
            if self.context.os_kind == "Windows":
                cmd = f"{venv_path}\\Scripts\\activate && {cmd}"
            else:
                cmd = f"source {venv_path}/bin/activate && {cmd}"
        
        # Database execution
        if cmd == "SELECT_QUERY" and self.context.db_type:
            if self.context.db_type == "postgres":
                db_user = self.context.db_user or "postgres"
                database = self.context.database or "postgres"
                db_host = self.context.db_host or "localhost"
                # This would need the actual query extracted from the original query
                cmd = f"psql -U {db_user} -d {database} -h {db_host} -c '<query>'"
        
        return cmd
    
    def _calculate_confidence(self, base_cmd: str) -> float:
        """
        Calculate confidence score based on context completeness and command specificity.
        Returns float between 0.0 and 1.0.
        """
        confidence = 0.7  # Base confidence
        
        # Increase confidence if we have rich context
        if self.context.execution != "local":
            if self.context.execution == "remote" and self.context.host and self.context.user:
                confidence += 0.15
            elif self.context.execution == "docker" and self.context.container:
                confidence += 0.15
            elif self.context.execution == "cloud" and self.context.cloud_provider:
                confidence += 0.10
        
        # Increase confidence for framework-specific commands
        if self.context.framework:
            confidence += 0.10
        
        # Decrease confidence for generic commands
        if base_cmd in ["ls -la", "dir", "pwd", "cd"]:
            confidence -= 0.05
        
        # Ensure confidence is in valid range
        return max(0.0, min(1.0, confidence))
    
    def _extract_subject(self, query: str, keyword: str) -> Optional[str]:
        match = re.search(rf"{keyword}\s+(?:named|called|labeled|named)?\s*([\w\.\-]+)", query)
        return match.group(1) if match else None

    def _extract_raw_path(self, query: str) -> Optional[str]:
        cleaned = re.sub(r"[?!.,]$", "", query).split()
        return cleaned[-1] if cleaned else None

class TerminalCommandAgent:
    """Main Agent orchestrator with strict validation."""
    def __init__(self, context: Optional[AgentContext] = None):
        if context is None:
            self.context = AgentContext()
        elif isinstance(context, dict):
            self.context = AgentContext(data=context)
        else:
            self.context = context
            
        self.planner = ExecutionPlanner(self.context)
        self.validator = SafetyValidator(self.context)

    def query(self, user_query: str) -> Dict[str, Any]:
        """
        Returns a structured JSON-compatible dictionary.
        Format: {
            "command": str,
            "explanation": str,
            "safety_status": "safe" | "unsafe" | "unknown",
            "confidence": float
        }
        """
        try:
            # 1. Basic Chaining Check
            if any(char in user_query for char in {";", "&&", "||", "|", "`", "$"}):
                return {
                    "command": "echo \"Invalid request\"",
                    "explanation": "Query contains forbidden chaining characters.",
                    "safety_status": "unsafe",
                    "confidence": 1.0
                }

            # 2. Execution Planning
            plan = self.planner.plan(user_query)
            intent = plan.get("intent")
            base_cmd = plan.get("base_command", "")
            confidence = plan.get("confidence", 0.0)
            
            # Handle code generation requests
            if intent == "CODE_REQUEST":
                return {
                    "command": "",
                    "explanation": "This appears to be a code generation request, not a shell command. Please clarify if you want me to: (1) generate code, or (2) execute a specific shell command.",
                    "safety_status": "unknown",
                    "requires_clarification": True,
                    "confidence": confidence
                }
            
            # Handle unclear intent
            if intent == "NEEDS_CLARIFICATION":
                return {
                    "command": "",
                    "explanation": "I couldn't determine what command you want to run. Could you please clarify? For example: 'list files', 'create directory named test', 'read file.txt', or 'search for pattern in files'.",
                    "safety_status": "unknown",
                    "requires_clarification": True,
                    "confidence": confidence
                }

            # 3. Environment Wrapping & Conflict Resolution
            final_cmd = self.planner.wrap_for_environment(base_cmd)
            
            if final_cmd == "SECURITY_REFUSED":
                return {
                    "command": "echo \"Security refused\"",
                    "explanation": "Command blocked by security policy.",
                    "safety_status": "unsafe",
                    "confidence": 1.0
                }

            # 4. Safety Validation
            is_safe = self.validator.is_safe(final_cmd)
            
            if not is_safe:
                return {
                    "command": "echo \"Unsafe command\"",
                    "explanation": f"The generated command '{final_cmd}' failed security validation.",
                    "safety_status": "unsafe",
                    "confidence": confidence
                }
            
            # 5. Success Response
            return {
                "command": final_cmd.strip(),
                "explanation": self._generate_explanation(final_cmd),
                "safety_status": "safe",
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Terminal Agent error: {e}")
            return {
                "command": "echo \"Internal error\"",
                "explanation": "An unexpected error occurred within the Terminal Agent.",
                "safety_status": "unknown"
            }

    def _generate_explanation(self, command: str) -> str:
        """Generates a human-readable explanation for the generated command."""
        cmd = command.lower().split()[0]
        explanations = {
            "ls": "Lists files and directories in the current path.",
            "dir": "Lists files and directories in the current path (Windows).",
            "pwd": "Shows the current working directory path.",
            "cd": "Changes or shows the current directory.",
            "mkdir": "Creates a new directory.",
            "touch": "Creates a new empty file.",
            "type": "Displays the contents of a file (Windows).",
            "cat": "Concatenates and displays file contents.",
            "grep": "Searches for patterns within files.",
            "findstr": "Searches for patterns within files (Windows).",
            "wc": "Counts lines, words, or characters in a file."
        }
        return explanations.get(cmd, f"Executes the {cmd} command.")
