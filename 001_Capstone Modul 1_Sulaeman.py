import os
import getpass
import json
import datetime
from tabulate import tabulate
from colorama import Fore, Style

users = {
    "1001": {"name": "Sulaeman", "role": "Manager", "password": "admin"},
    "1002": {"name": "Gerald", "role": "Team Member", "password": "member1"},
    "1003": {"name": "Rafdi", "role": "Team Member", "password": "member2"},
    "1004": {"name": "Aimar", "role": "Team Member", "password": "member3"}
}

projects = {}
recycle_bin = {}
login_log = []

def login():
    user_id = input("Masukkan ID Anda: ").strip()
    
    if user_id not in users:
        print("ID Pengguna tidak ditemukan.")
        return
    
    password = getpass.getpass("Masukkan Password: ")
    
    if password == users[user_id]["password"]:
        
        log_login(user_id)  
        
        user_data = users[user_id]
        name = user_data["name"]
        role = user_data["role"]
        print(f"Selamat datang, {name} ({role})!")
        return user_id, role  
    else:
        print("Password yang Anda masukkan salah. Silakan coba lagi.")
        return None, None

def save_projects():
    '''Save projects data to a JSON file'''
    with open('projects.json', 'w') as f:
        json.dump(projects, f, indent=4)

def load_projects():
    '''Load projects data from a JSON file if exists'''
    global projects
    if os.path.exists('projects.json'):
        with open('projects.json', 'r') as f:
            projects = json.load(f)

def show_main_menu(role):
    '''Menampilkan Menu Berdasarkan Peran'''
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(Fore.CYAN + "\n=====Project Tracker=====" + Style.RESET_ALL)
    
    menu_items = []
    
    if role == "Manager":
        menu_items = [
            ["1", "Tambah Project (Create)"],
            ["2", "Lihat Project (Read)"],
            ["3", "Update Project (Update)"],
            ["4", "Hapus Project (Delete)"],
            ["5", "Lihat Daftar Pekerja"],
            ["6", "Tambahkan Jobdesc Project Ke Team Member"],
            ["7", "Lihat Recyle Bin"],
            ["8", "Data Log Pengguna"],
            ["9", "Keluar"]
        ]
    elif role == "Team Member":
        menu_items = [
            ["1", "Lihat Project (Read)"],
            ["2", "Lihat Tugas yang Diberikan"],
            ["3", "Keluar"]
        ]
    
    print(tabulate(menu_items, headers=["Pilihan", "Deskripsi"], tablefmt="grid"))

def create_project(user_id):
    '''Menambahkan Project Baru'''
    project_id = input("Masukkan ID Project: ").strip()
    
    if project_id in projects:
        print("ID Project sudah ada")
        return
    
    name = input("Masukkan Nama Project: ").strip()
    deadline = input("Masukkan Deadline Project (YYYY-MM-DD): ").strip()
    status = input("Masukkan Status Project (Belum Dimulai/ Berjalan/ Selesai): ").strip()

    projects[project_id] = {
        "name": name,
        "deadline": deadline,
        "status": status,
        "owner" : user_id,
        "assigned_members" : [],
        "tasks" : {}
    }
    print("Project Berhasil Ditambahkan!")
    save_projects()


def read_project():
    '''Menampilkan Semua Project'''
    if not projects:
        print("Belum ada Project")
        return
        
    project_data = []
    for project_id, project in projects.items():
        countdown = calculate_deadline_countdown(project.get('deadline', "Not Set"))
        assigned_members = project.get('assigned_members', [])
    
        team_members = ', '.join([users[member_id]['name'] for member_id in assigned_members if member_id in users]) if assigned_members else "Tidak ada anggota"
        
        tasks = ', '.join([task["Name"] for task in project.get("tasks", {}).values()])
        total_tasks = len(project.get("tasks", {}))
        completed_tasks = sum(1 for task in project.get("tasks", {}).values() if task["Status"] == "Selesai")
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        project_data.append([ 
            project_id, 
            project['name'], 
            project['deadline'], 
            countdown, 
            project['status'], 
            project['owner'],
            tasks,  
            team_members,  
            f"{progress:.2f}%"
        ])

    headers = ["ID Project", "Nama Project", "Deadline Project", "Countdown", "Status Project", "Owner", "Pekerjaan", "Team Members", "Progress"]
    print(tabulate(project_data, headers, tablefmt="grid"))

def calculate_deadline_countdown(deadline):
    '''Calculate the remaining time until the deadline'''
    try:
        deadline_date = datetime.datetime.strptime(deadline, "%Y-%m-%d")
        remaining_time = deadline_date - datetime.datetime.now()
        if remaining_time.days < 0:
            return f"{Fore.RED}Terlambat {abs(remaining_time.days)} hari{Style.RESET_ALL}"
        return f"{Fore.GREEN}{remaining_time.days} hari tersisa{Style.RESET_ALL}"
    except ValueError:
        return "Tanggal tidak valid"

def update_project(user_id, role):
    '''Memperbarui Status Project'''
    project_id = input("Masukkan ID Project yang akan diperbarui: ").strip()
    
    if project_id not in projects:
        print("ID Project tidak ditemukan")
        return
    
    if role == "Team Member" and projects[project_id]["owner"] != user_id:
        print("Anda tidak bisa memperbarui project ini karena Anda bukan pemiliknya.")
        return
    
    status = input("Masukkan Status Project Baru (Belum Dimulai/ Berjalan/ Selesai): ").strip()
    if status not in ["Belum Dimulai", "Berjalan", "Selesai"]:
        print("Status tidak valid. Pilih dari: Belum Dimulai, Berjalan, atau Selesai.")
        return

    projects[project_id]["status"] = status
    print("Status Project Berhasil Diperbarui!")
    save_projects()

def delete_project():
    '''Menghapus Project'''
    project_id = input("Masukkan ID Project yang akan dihapus: ").strip()
    
    if project_id not in projects:
        print("ID Project tidak ditemukan")
        return

    recycle_bin[project_id] = projects.pop(project_id)
    print("Project Berhasil Dihapus!")
    save_projects()

def show_employee_list():
    '''Menampilkan Daftar Karyawan'''
    print("\n===== Daftar Karyawan =====")
    employee_list = [[emp_id, data["name"], data["role"]] for emp_id, data in users.items()]
    print(tabulate(employee_list, headers=["ID", "Nama", "Peran"], tablefmt="grid"))

def add_and_assign_task_to_project():
    project_id = input("Masukkan ID Project untuk menambahkan dan menugaskan tugas: ").strip()
    
    if project_id not in projects:
        print(f"Project dengan ID {project_id} tidak ditemukan.")
        return
    
    task_name = input("Masukkan Nama Tugas: ").strip()
    task_description = input("Masukkan Deskripsi Tugas: ").strip()

    task_id = f"T-{len(projects[project_id]['tasks']) + 1}"

    projects[project_id]["tasks"][task_id] = {
        "Name": task_name,
        "Description": task_description,
        "Status": "Belum Dimulai",
        "Assigned To": None
    }
    print(f"Tugas '{task_name}' berhasil ditambahkan ke dalam project {projects[project_id]['name']}")

    print("\nDaftar Karyawan:")
    for user_id, user in users.items():
        print(f"{user_id}: {user['name']} - {user['role']}")

    member_id = input("Masukkan ID Anggota yang akan ditugaskan ke tugas: ").strip()
    
    if member_id not in users:
        print(f"Anggota dengan ID {member_id} tidak ditemukan.")
        return

    projects[project_id]["tasks"][task_id]["Assigned To"] = member_id
    print(f"Tugas '{projects[project_id]['tasks'][task_id]['Name']}' berhasil ditugaskan ke {users[member_id]['name']}")

    if member_id not in projects[project_id]["assigned_members"]:
        projects[project_id]["assigned_members"].append(member_id)
    
    save_projects()

def view_and_update_task(user_id):
    '''Menampilkan dan Memperbarui Status Tugas yang Ditugaskan kepada Team Member'''
    assigned_tasks = []
    task_mapping = {}
    
    for project_id, project in projects.items():
        total_tasks = 0
        completed_tasks = 0
        for task_id, task in project["tasks"].items():
            if task["Assigned To"] == user_id:
                assigned_tasks.append([
                    project_id,
                    project["name"],
                    task_id,
                    task["Name"],
                    task["Status"],
                    task["Description"]
                ])
                task_mapping[task_id] = (project_id, task)
            
            total_tasks += 1
            if task["Status"] == "Selesai":
                completed_tasks += 1
        
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        for task in assigned_tasks:
            if task[0] == project_id:
                task.append(f"{progress:.2f}%")
    
    if not assigned_tasks:
        print("Anda belum memiliki tugas yang ditugaskan.")
        input("Tekan Enter untuk melanjutkan...")
        return
    
    headers = ["ID Project", "Nama Project", "ID Tugas", "Tugas", "Status", "Deskripsi", "Progress"]
    print(tabulate(assigned_tasks, headers, tablefmt="grid"))
    
    task_id = input("Masukkan ID Tugas yang akan diperbarui (atau tekan Enter untuk keluar): ").strip()
    if not task_id:
        return
    
    if task_id not in task_mapping:
        print("Tugas tidak valid atau bukan milik Anda.")
        return
    
    status = input("Masukkan Status Baru (Belum Dimulai/ Berjalan/ Selesai): ").strip()
    if status not in ["Belum Dimulai", "Berjalan", "Selesai"]:
        print("Status tidak valid.")
        return
    
    project_id, task = task_mapping[task_id]
    task["Status"] = status
    print(f"Status tugas '{task['Name']}' diperbarui menjadi {status}.")
    save_projects()
    
    input("Tekan Enter untuk melanjutkan...")

def restore_project():
    if not recycle_bin:
        print("Recycle Bin Kosong")
        return
    print("\n=====Daftar Project di Recycle Bin")
    project_data = [[pid, p['name'], p['deadline'], p['status'], p['owner']] for pid, p in recycle_bin.items()]
    print(tabulate(project_data, ["ID Project", "Nama Project", "Deadline", "Status", "Owner"], tablefmt="grid"))
    project_id = input("\nMasukkan ID Project yang ingin di-restore: ").strip()
    if project_id in recycle_bin:
        projects[project_id] = recycle_bin.pop(project_id)
        print(f"Project dengan ID '{project_id}' berhasil dipulihkan!")
    else:
        print("ID Project tidak ditemukan di Recycle Bin.")

def log_login(user_id):
    '''Mencatat login pengguna ke dalam log'''
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    login_log.append({"user_id": user_id, "timestamp": timestamp})
    print(f"{users[user_id]['name']} berhasil login pada {timestamp}")

def view_login_backlog():
    '''Menampilkan backlog login'''
    if not login_log:
        print("Tidak ada data login.")
        return
    
    print("\n===== Backlog Login =====")
    backlog_data = []
    for log in login_log:
        user_name = users[log["user_id"]]["name"]
        backlog_data.append([user_name, log["timestamp"]])

    print(tabulate(backlog_data, headers=["Nama Pengguna", "Waktu Login"], tablefmt="grid"))

def main():
    '''Main Program'''
    load_projects()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=====LOGIN=====")
        user_id, role = login()  
        
        if not user_id:
            continue  

        while True:
            show_main_menu(role)
            pilihan = input("\nPilihan Menu: ").strip()
            
            if role == "Manager":
                if pilihan == "1":
                    print("\n=====Tambah Project=====")
                    create_project(user_id)
                elif pilihan == "2":
                    print("\n=====Lihat Project=====")
                    read_project()
                elif pilihan == "3":
                    print("\n=====Update Project=====")
                    read_project()
                    update_project(user_id, role)
                elif pilihan == "4":
                    print("\n=====Hapus Project=====")
                    read_project()
                    delete_project()
                elif pilihan == "5":
                    print("\n=====List Karyawan=====")
                    show_employee_list()
                elif pilihan == "6":
                    print("\n=====Tambahkan Jobdesc Project Ke Team Member=====")
                    read_project()
                    add_and_assign_task_to_project()
                elif pilihan == "7":
                    print("\n=====Recycle Bin=====")
                    restore_project() 
                elif pilihan == "8":
                    print("\n=====Data Log Pengguna=====")
                    view_login_backlog()  
                elif pilihan == "9":
                    print("\n=====Keluar=====")
                    break
                else:
                    print("Pilihan yang Anda masukkan salah. Silakan coba lagi.")
            
            elif role == "Team Member":
                if pilihan == "1":
                    print("\n=====Lihat Project=====")
                    read_project()
                elif pilihan == "2":
                    print("\n=====Lihat Tugas Saya=====")
                    view_and_update_task(user_id)
                elif pilihan == "3":
                    print("\n=====Keluar=====")
                    break
                else:
                    print("Pilihan yang Anda masukkan salah. Silakan coba lagi.")
            
            input("\nTekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    main()
