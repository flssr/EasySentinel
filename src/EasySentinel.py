import tkinter as tk
import subprocess
import sys
import json
import os

class CMDTool:
    # 确保配置文件保存在程序所在目录
    # 处理PyInstaller打包后的情况
    if hasattr(sys, '_MEIPASS'):
        # 打包后，将配置文件保存在可执行文件所在目录
        CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "config.json")
    else:
        # 开发环境，保存在脚本所在目录
        CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    
    def __init__(self, root):
        self.root = root
        self.root.title("EasySentinel")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # 默认配置
        self.full_command = "java -Dserver.port={port} -Dcsp.sentinel.dashboard.server={report_addr} -Dproject.name=sentinel-dashboard -jar sentinel-dashboard.jar"
        self.default_port = "8078"
        self.default_report_addr = "localhost:8079"
        
        # 添加菜单栏
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)
        
        # 添加设置菜单
        setting_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="设置", menu=setting_menu)
        setting_menu.add_command(label="编辑完整命令", command=self.edit_full_command)

        
        # 运行端口输入
        self.port_label = tk.Label(root, text="运行端口:", bg="white", fg="black", bd=0)
        self.port_label.pack(pady=5)
        
        self.port_var = tk.StringVar(value=self.default_port)  # 使用加载的或默认端口
        self.port_entry = tk.Entry(root, textvariable=self.port_var, width=30, bg="#ffffff", bd=1, highlightthickness=0)
        self.port_entry.pack(pady=5)
        
        # 客户端上报地址输入
        self.report_addr_label = tk.Label(root, text="客户端上报地址:", bg="white", fg="black", bd=0)
        self.report_addr_label.pack(pady=5)
        
        self.report_addr_var = tk.StringVar(value=self.default_report_addr)  # 使用加载的或默认上报地址
        self.report_addr_entry = tk.Entry(root, textvariable=self.report_addr_var, width=30, bg="#ffffff", bd=1, highlightthickness=0)
        self.report_addr_entry.pack(pady=5)
        
        # 加载配置（在创建所有变量后）
        self.load_config()
        
        # 运行按钮
        self.run_button = tk.Button(root, text="运行命令", command=self.run_cmd, width=20, bg="#ffffff", fg="black", bd=1, highlightthickness=0)
        self.run_button.pack(pady=20)
        
        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = tk.Label(root, textvariable=self.status_var, fg="green", bg="#ffffff", bd=0)
        self.status_label.pack(pady=10)
        
        # 提高组件层级，确保在背景图上方显示
        self.port_label.lift()
        self.port_entry.lift()
        self.report_addr_label.lift()
        self.report_addr_entry.lift()
        self.run_button.lift()
        self.status_label.lift()
        
        # 确保配置文件存在，保存默认配置
        if not os.path.exists(self.CONFIG_FILE):
            self.save_config()


    def edit_full_command(self):
        """打开对话框修改完整命令"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑完整命令")
        dialog.geometry("450x150")
        dialog.resizable(False, False)
        
        # 添加标签
        label = tk.Label(dialog, text="完整命令:")
        label.pack(pady=10)
        
        # 添加文本框
        cmd_var = tk.StringVar(value=self.full_command)
        text = tk.Text(dialog, height=4, width=50)
        text.pack(pady=5)
        text.insert(1.0, self.full_command)
        
        # 添加按钮
        def save_command():
            self.full_command = text.get(1.0, tk.END).strip()
            self.save_config()  # 保存配置
            dialog.destroy()
        
        save_btn = tk.Button(dialog, text="保存", command=save_command)
        save_btn.pack(side=tk.LEFT, padx=20, pady=10)
        
        cancel_btn = tk.Button(dialog, text="取消", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=20, pady=10)
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'full_command' in config:
                        self.full_command = config['full_command']
                    if 'port' in config:
                        self.default_port = config['port']
                        # 如果port_var已初始化，更新它
                        if hasattr(self, 'port_var'):
                            self.port_var.set(config['port'])
                    if 'report_addr' in config:
                        self.default_report_addr = config['report_addr']
                        # 如果report_addr_var已初始化，更新它
                        if hasattr(self, 'report_addr_var'):
                            self.report_addr_var.set(config['report_addr'])
            except Exception as e:
                print(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            'full_command': self.full_command,
            'port': self.port_var.get(),
            'report_addr': self.report_addr_var.get()
        }
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def run_cmd(self):
        try:
            port = self.port_var.get()
            report_addr = self.report_addr_var.get()
            # 使用用户定义的完整命令，替换{port}和{report_addr}占位符
            cmd = self.full_command.replace("{port}", port).replace("{report_addr}", report_addr)
            
            self.status_var.set(f"正在运行: {cmd}")
            self.status_label.config(fg="blue")
            
            # 保存配置
            self.save_config()
            
            # 在新的cmd窗口中运行命令
            subprocess.Popen(f'start cmd /k "{cmd}"', shell=True)
            
            self.status_var.set(f"命令已在新窗口启动: {cmd}")
            self.status_label.config(fg="green")
        except Exception as e:
            self.status_var.set(f"异常: {str(e)}")
            self.status_label.config(fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    # 设置窗口图标
    try:
        # 处理打包后的情况
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, 'sentinel-icon.ico')
        else:
            icon_path = 'sentinel-icon.ico'
        root.iconbitmap(icon_path)
    except:
        pass
    app = CMDTool(root)
    root.mainloop()
