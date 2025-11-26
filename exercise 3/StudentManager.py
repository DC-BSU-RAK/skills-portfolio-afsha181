import os
import csv
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog

# ----------------- Path handling -----------------


def get_default_data_file():
    """
    Return a safe, portable default path for the data file.
    - Prefer the folder where this script is located.
    - Fall back to current working directory if __file__ is not available.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not base_dir:
            raise Exception
    except Exception:
        # Fallback: where the program is run from
        base_dir = os.getcwd()

    return os.path.join(base_dir, 'student_info.txt')


# Defaults & constants (must be defined before functions that use them)
DEFAULT_DATA_FILE = get_default_data_file()
POSSIBLE_TOTAL = 160  # coursework total (3*20) + exam (100) => 160


# ----------------- File utilities -----------------


def init_data_file(path=DEFAULT_DATA_FILE):
    """Ensure directory and file exist. If missing, initialize with 0 count."""
    dirn = os.path.dirname(path) or '.'
    os.makedirs(dirn, exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'w', newline='') as fh:
            fh.write('0\n')


def read_records(path=DEFAULT_DATA_FILE):
    """Return list of records where each record is a dict with keys:
    id(int), fullname(str), cw_a(int), cw_b(int), cw_c(int), exam(int)
    """
    init_data_file(path)
    records = []
    with open(path, 'r', newline='') as fh:
        reader = csv.reader(fh)
        rows = [r for r in reader if r]
    if not rows:
        return []
    # If first row is single integer, treat as count header
    start = 0
    if len(rows[0]) == 1 and rows[0][0].strip().isdigit():
        start = 1
    for row in rows[start:]:
        row = [c.strip() for c in row]
        if len(row) < 6:
            continue
        try:
            rid = int(row[0])
            name = row[1]
            ca = int(row[2])
            cb = int(row[3])
            cc = int(row[4])
            exam = int(row[5])
            records.append(
                {
                    'id': rid,
                    'fullname': name,
                    'cw_a': ca,
                    'cw_b': cb,
                    'cw_c': cc,
                    'exam': exam,
                }
            )
        except ValueError:
            continue
    return records


def write_records(records, path=DEFAULT_DATA_FILE):
    """Overwrite file with current list of records. Writes count header first."""
    dirn = os.path.dirname(path) or '.'
    os.makedirs(dirn, exist_ok=True)
    with open(path, 'w', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow([len(records)])
        for r in records:
            writer.writerow(
                [r['id'], r['fullname'], r['cw_a'], r['cw_b'], r['cw_c'], r['exam']]
            )


# ----------------- Business helpers -----------------


def cw_sum(rec):
    return rec['cw_a'] + rec['cw_b'] + rec['cw_c']


def compute_percentage(rec):
    tot = cw_sum(rec) + rec['exam']
    if POSSIBLE_TOTAL <= 0:
        return 0.0
    return (tot / POSSIBLE_TOTAL) * 100.0


def grade_from_percentage(pct):
    if pct >= 70:
        return 'A'
    if pct >= 60:
        return 'B'
    if pct >= 50:
        return 'C'
    if pct >= 40:
        return 'D'
    return 'F'


# ----------------- GUI application -----------------


class MarksManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Marks Manager')
        self.geometry('920x620')

        # Use portable default path
        self.data_file = DEFAULT_DATA_FILE
        self.records = read_records(self.data_file)

        self._build_menu()
        self._build_widgets()
        self._update_status()

    # ---------- build UI ----------
    def _build_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)

        rec_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Records', menu=rec_menu)
        rec_menu.add_command(label='List all', command=self.show_all)
        rec_menu.add_command(label='Find single', command=self.show_single)
        rec_menu.add_separator()
        rec_menu.add_command(label='Top performer', command=self.show_top)
        rec_menu.add_command(label='Lowest performer', command=self.show_bottom)
        rec_menu.add_separator()
        rec_menu.add_command(label='Sort (A/D)', command=self.sort_by_pct)
        rec_menu.add_command(label='Add record', command=self.add_record)
        rec_menu.add_command(label='Remove record', command=self.remove_record)
        rec_menu.add_command(label='Edit record', command=self.edit_record)
        rec_menu.add_separator()
        rec_menu.add_command(label='Reload file', command=self.reload_from_disk)
        rec_menu.add_command(label='Save file', command=self.save_to_disk)

        fmenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='File', menu=fmenu)
        fmenu.add_command(label='Open data file...', command=self.open_file_dialog)
        fmenu.add_command(label='Quit', command=self.quit)

        hmenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Help', menu=hmenu)
        hmenu.add_command(label='About', command=self._about)

    def _build_widgets(self):
        self.output = tk.Text(self, wrap='none')
        self.output.pack(fill='both', expand=True)

        xbar = ttk.Scrollbar(self, orient='horizontal', command=self.output.xview)
        xbar.pack(side='bottom', fill='x')
        ybar = ttk.Scrollbar(self, orient='vertical', command=self.output.yview)
        ybar.pack(side='right', fill='y')
        self.output.configure(xscrollcommand=xbar.set, yscrollcommand=ybar.set)

        self.status_var = tk.StringVar()
        status_label = ttk.Label(self, textvariable=self.status_var, anchor='w')
        status_label.pack(side='bottom', fill='x')

    def _update_status(self, msg=None):
        if msg:
            self.status_var.set(msg)
        else:
            self.status_var.set(f'{len(self.records)} record(s) loaded')

    # ---------- display helpers ----------
    def _clear(self):
        self.output.delete('1.0', tk.END)

    def _print(self, text=''):
        self.output.insert(tk.END, text + '\n')

    def _print_record(self, rec):
        self._print(f"Full name: {rec['fullname']}")
        self._print(f"Student ID: {rec['id']}")
        self._print(f"Coursework total: {cw_sum(rec)} / 60")
        self._print(f"Exam: {rec['exam']} / 100")
        pct = compute_percentage(rec)
        self._print(f"Overall: {pct:.2f}%")
        self._print(f"Grade: {grade_from_percentage(pct)}")
        self._print('')

    # ---------- file/menu actions ----------
    def reload_from_disk(self):
        self.records = read_records(self.data_file)
        self._update_status('Data reloaded from disk')
        messagebox.showinfo('Reload', 'Records reloaded from file.')

    def save_to_disk(self):
        write_records(self.records, self.data_file)
        self._update_status('Records saved to disk')
        messagebox.showinfo('Saved', f'Data written to {self.data_file}')

    def open_file_dialog(self):
        path = filedialog.askopenfilename(
            title='Open data file',
            filetypes=[('Text', '*.txt'), ('CSV', '*.csv'), ('All', '*.*')],
        )
        if path:
            self.data_file = path
            self.reload_from_disk()

    def _about(self):
        messagebox.showinfo(
            'About', 'Marks Manager - refactored student manager example'
        )

    # ---------- operations ----------
    def _find_by_id(self, sid):
        for r in self.records:
            if r['id'] == sid:
                return r
        return None

    def _find_by_name(self, fragment):
        return [r for r in self.records if fragment.lower() in r['fullname'].lower()]

    def show_all(self):
        self._clear()
        if not self.records:
            self._print('No records present.')
            return
        total = 0.0
        for r in self.records:
            self._print_record(r)
            total += compute_percentage(r)
        avg = total / len(self.records)
        self._print('--- Summary ---')
        self._print(f"Count: {len(self.records)}")
        self._print(f"Average: {avg:.2f}%")
        self._update_status('Viewing all records')

    def show_single(self):
        if not self.records:
            messagebox.showwarning('Empty', 'No data loaded')
            return
        key = simpledialog.askstring('Find', 'Enter student ID or part of name:')
        if not key:
            return
        key = key.strip()
        try:
            sid = int(key)
            rec = self._find_by_id(sid)
            if not rec:
                messagebox.showinfo('Not found', f'No record with ID {sid}')
                return
            self._clear()
            self._print_record(rec)
            self._update_status(f'Viewing {rec["id"]}')
            return
        except ValueError:
            matches = self._find_by_name(key)
            if not matches:
                messagebox.showinfo('Not found', 'No matching names')
                return
            if len(matches) == 1:
                self._clear()
                self._print_record(matches[0])
                self._update_status(f'Viewing {matches[0]["id"]}')
                return
            sel = self._choose(matches, title='Choose record')
            if sel is None:
                return
            rec = matches[sel]
            self._clear()
            self._print_record(rec)
            self._update_status(f'Viewing {rec["id"]}')

    def _choose(self, items, title='Choose'):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.grab_set()
        tk.Label(dlg, text='Select:').pack(padx=8, pady=6)
        lb = tk.Listbox(dlg, width=60, height=10)
        lb.pack(padx=8, pady=6)
        for it in items:
            lb.insert(tk.END, f"{it['id']} - {it['fullname']}")
        res = {'idx': None}

        def ok():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning('Pick', 'Please select an item')
                return
            res['idx'] = sel[0]
            dlg.destroy()

        def cancel():
            dlg.destroy()

        btnf = tk.Frame(dlg)
        btnf.pack(pady=6)
        ttk.Button(btnf, text='OK', command=ok).pack(side='left', padx=4)
        ttk.Button(btnf, text='Cancel', command=cancel).pack(side='left', padx=4)
        self.wait_window(dlg)
        return res['idx']

    def show_top(self):
        if not self.records:
            messagebox.showwarning('Empty', 'No data loaded')
            return
        best = max(self.records, key=lambda r: compute_percentage(r))
        self._clear()
        self._print('--- Top performer ---')
        self._print_record(best)
        self._update_status(f'Top: {best["id"]} - {best["fullname"]}')

    def show_bottom(self):
        if not self.records:
            messagebox.showwarning('Empty', 'No data loaded')
            return
        worst = min(self.records, key=lambda r: compute_percentage(r))
        self._clear()
        self._print('--- Lowest performer ---')
        self._print_record(worst)
        self._update_status(f'Lowest: {worst["id"]} - {worst["fullname"]}')

    def sort_by_pct(self):
        if not self.records:
            messagebox.showwarning('Empty', 'No data loaded')
            return
        choice = simpledialog.askstring(
            'Sort', 'Enter A for ascending or D for descending:'
        )
        if not choice:
            return
        c = choice.strip().upper()
        if c not in ('A', 'D'):
            messagebox.showerror('Bad', 'Enter A or D')
            return
        rev = c == 'D'
        self.records.sort(key=lambda r: compute_percentage(r), reverse=rev)
        self.show_all()
        self._update_status(f'Sorted ({"desc" if rev else "asc"})')

    def add_record(self):
        dlg = RecordEditor(self, title='Add record')
        self.wait_window(dlg)
        if dlg.result:
            new = dlg.result
            if any(r['id'] == new['id'] for r in self.records):
                messagebox.showerror('Duplicate', 'ID already exists')
                return
            self.records.append(new)
            write_records(self.records, self.data_file)
            self._update_status(f'Record {new["id"]} added')
            messagebox.showinfo('Added', 'Record added and saved')

    def remove_record(self):
        if not self.records:
            messagebox.showwarning('Empty', 'No data loaded')
            return
        key = simpledialog.askstring(
            'Remove', 'Enter student ID or part of name to remove:'
        )
        if not key:
            return
        key = key.strip()
        try:
            sid = int(key)
            rec = self._find_by_id(sid)
            if not rec:
                messagebox.showinfo('Not found', f'No record with ID {sid}')
                return
            if messagebox.askyesno(
                'Confirm', f'Remove {rec["id"]} - {rec["fullname"]}?'
            ):
                self.records = [r for r in self.records if r['id'] != sid]
                write_records(self.records, self.data_file)
                self._update_status(f'Record {sid} removed')
                messagebox.showinfo('Removed', 'Record removed and saved')
            return
        except ValueError:
            matches = self._find_by_name(key)
            if not matches:
                messagebox.showinfo('Not found', 'No matching names')
                return
            if len(matches) == 1:
                rec = matches[0]
                if messagebox.askyesno(
                    'Confirm', f'Remove {rec["id"]} - {rec["fullname"]}?'
                ):
                    self.records = [
                        r for r in self.records if r['id'] != rec['id']
                    ]
                    write_records(self.records, self.data_file)
                    self._update_status(f'Record {rec["id"]} removed')
                    messagebox.showinfo('Removed', 'Record removed and saved')
                return
            sel = self._choose(matches, title='Choose to remove')
            if sel is None:
                return
            rec = matches[sel]
            if messagebox.askyesno(
                'Confirm', f'Remove {rec["id"]} - {rec["fullname"]}?'
            ):
                self.records = [r for r in self.records if r['id'] != rec['id']]
                write_records(self.records, self.data_file)
                self._update_status(f'Record {rec["id"]} removed')
                messagebox.showinfo('Removed', 'Record removed and saved')

    def edit_record(self):
        if not self.records:
            messagebox.showwarning('Empty', 'No data loaded')
            return
        key = simpledialog.askstring(
            'Edit', 'Enter student ID or part of name to edit:'
        )
        if not key:
            return
        key = key.strip()
        try:
            sid = int(key)
            rec = self._find_by_id(sid)
            if not rec:
                messagebox.showinfo('Not found', f'No record with ID {sid}')
                return
            dlg = RecordEditor(self, student=rec, title='Edit record')
            self.wait_window(dlg)
            if dlg.result:
                new = dlg.result
                for i, r in enumerate(self.records):
                    if r['id'] == sid:
                        self.records[i] = new
                        break
                write_records(self.records, self.data_file)
                self._update_status(f'Record {new["id"]} updated')
                messagebox.showinfo('Updated', 'Record updated and saved')
            return
        except ValueError:
            matches = self._find_by_name(key)
            if not matches:
                messagebox.showinfo('Not found', 'No matching names')
                return
            if len(matches) == 1:
                rec = matches[0]
                dlg = RecordEditor(self, student=rec, title='Edit record')
                self.wait_window(dlg)
                if dlg.result:
                    new = dlg.result
                    for i, r in enumerate(self.records):
                        if r['id'] == rec['id']:
                            self.records[i] = new
                            break
                    write_records(self.records, self.data_file)
                    self._update_status(f'Record {new["id"]} updated')
                    messagebox.showinfo('Updated', 'Record updated and saved')
                return
            sel = self._choose(matches, title='Choose to edit')
            if sel is None:
                return
            rec = matches[sel]
            dlg = RecordEditor(self, student=rec, title='Edit record')
            self.wait_window(dlg)
            if dlg.result:
                new = dlg.result
                for i, r in enumerate(self.records):
                    if r['id'] == rec['id']:
                        self.records[i] = new
                        break
                write_records(self.records, self.data_file)
                self._update_status(f'Record {new["id"]} updated')
                messagebox.showinfo('Updated', 'Record updated and saved')


class RecordEditor(tk.Toplevel):
    def __init__(self, parent, student=None, title='Edit'):
        super().__init__(parent)
        self.title(title)
        self.grab_set()
        self.result = None

        ttk.Label(self, text='Student ID (1000-9999):').grid(
            row=0, column=0, sticky='e', padx=4, pady=4
        )
        self.f_id = ttk.Entry(self)
        self.f_id.grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(self, text='Full name:').grid(
            row=1, column=0, sticky='e', padx=4, pady=4
        )
        self.f_name = ttk.Entry(self, width=40)
        self.f_name.grid(row=1, column=1, padx=4, pady=4)

        ttk.Label(self, text='CW 1 (0-20):').grid(
            row=2, column=0, sticky='e', padx=4, pady=4
        )
        self.f_cw1 = ttk.Entry(self)
        self.f_cw1.grid(row=2, column=1, padx=4, pady=4)

        ttk.Label(self, text='CW 2 (0-20):').grid(
            row=3, column=0, sticky='e', padx=4, pady=4
        )
        self.f_cw2 = ttk.Entry(self)
        self.f_cw2.grid(row=3, column=1, padx=4, pady=4)

        ttk.Label(self, text='CW 3 (0-20):').grid(
            row=4, column=0, sticky='e', padx=4, pady=4
        )
        self.f_cw3 = ttk.Entry(self)
        self.f_cw3.grid(row=4, column=1, padx=4, pady=4)

        ttk.Label(self, text='Exam (0-100):').grid(
            row=5, column=0, sticky='e', padx=4, pady=4
        )
        self.f_exam = ttk.Entry(self)
        self.f_exam.grid(row=5, column=1, padx=4, pady=4)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text='OK', command=self._on_ok).pack(
            side='left', padx=6
        )
        ttk.Button(btn_frame, text='Cancel', command=self._on_cancel).pack(
            side='left', padx=6
        )

        if student:
            self.f_id.insert(0, str(student['id']))
            self.f_name.insert(0, student['fullname'])
            self.f_cw1.insert(0, str(student['cw_a']))
            self.f_cw2.insert(0, str(student['cw_b']))
            self.f_cw3.insert(0, str(student['cw_c']))
            self.f_exam.insert(0, str(student['exam']))

    def _on_ok(self):
        try:
            sid = int(self.f_id.get())
            if not (1000 <= sid <= 9999):
                raise ValueError('ID must be between 1000 and 9999')
            name = self.f_name.get().strip()
            if not name:
                raise ValueError('Name required')
            cw1 = int(self.f_cw1.get())
            cw2 = int(self.f_cw2.get())
            cw3 = int(self.f_cw3.get())
            for cw in (cw1, cw2, cw3):
                if not (0 <= cw <= 20):
                    raise ValueError('Coursework marks must be 0-20')
            exam = int(self.f_exam.get())
            if not (0 <= exam <= 100):
                raise ValueError('Exam must be 0-100')
            self.result = {
                'id': sid,
                'fullname': name,
                'cw_a': cw1,
                'cw_b': cw2,
                'cw_c': cw3,
                'exam': exam,
            }
            self.destroy()
        except ValueError as ex:
            messagebox.showerror('Invalid', f'Invalid input: {ex}')

    def _on_cancel(self):
        self.destroy()


if __name__ == '__main__':
    app = MarksManager()
    app.mainloop()
