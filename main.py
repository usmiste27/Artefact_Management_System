"""Tkinter graphical Artefact Management System."""

import json
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk


artefacts = []
VALID_CONDITIONS = ("Good", "Damaged", "Under Repair")
DATA_FILE = Path(__file__).resolve().parent / "artefacts.json"


SAMPLE_ARTEFACTS = [
    {"id": "ART001", "name": "Old Photograph", "category": "Photograph",
     "location": "Display Case B", "condition": "Good",
     "description": "Historical photograph from 1940.", "acquisition_date": "12-05-2020"},
    {"id": "ART002", "name": "Historical Handwritten Letter", "category": "Document",
     "location": "Archive Cabinet 1", "condition": "Damaged",
     "description": "Letter describing local events.", "acquisition_date": "18-08-2018"},
    {"id": "ART003", "name": "Antique Clock", "category": "Clock",
     "location": "Main Hall Shelf", "condition": "Under Repair",
     "description": "Mechanical clock from the early twentieth century.", "acquisition_date": "03-11-2019"},
    {"id": "ART004", "name": "Traditional Pottery", "category": "Pottery",
     "location": "Ceramics Gallery", "condition": "Good",
     "description": "Handmade traditional clay vessel.", "acquisition_date": "25-04-2021"},
    {"id": "ART005", "name": "Historical Newspaper", "category": "Document",
     "location": "Reading Room", "condition": "Under Repair",
     "description": "Newspaper edition covering a local historic event.", "acquisition_date": "10-09-2017"},
    {"id": "ART006", "name": "Vintage Coin", "category": "Coin",
     "location": "Coin Display A", "condition": "Good",
     "description": "Silver coin issued in the nineteenth century.", "acquisition_date": "06-02-2022"},
    {"id": "ART007", "name": "Old Map", "category": "Map",
     "location": "Map Cabinet", "condition": "Damaged",
     "description": "Map showing historical county boundaries.", "acquisition_date": "14-07-2016"},
    {"id": "ART008", "name": "Traditional Musical Instrument", "category": "Instrument",
     "location": "Music Gallery", "condition": "Good",
     "description": "Locally made traditional musical instrument.", "acquisition_date": "22-12-2020"},
]


def generate_artefact_id():
    """Return the next available unique artefact ID."""
    numbers = []
    for record in artefacts:
        artefact_id = record.get("id", "")
        if artefact_id.startswith("ART"):
            try:
                numbers.append(int(artefact_id[3:]))
            except (TypeError, ValueError):
                pass
    return "ART" + str(max(numbers, default=0) + 1).zfill(3)


def validate_condition(condition):
    """Return True only when condition is a permitted value."""
    return condition in VALID_CONDITIONS


def find_artefact_by_id(artefact_id):
    """Return the matching dictionary, or None if it does not exist."""
    for record in artefacts:
        if record["id"].upper() == artefact_id.strip().upper():
            return record
    return None


def save_artefacts():
    """Save the in-memory collection to JSON."""
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(artefacts, file, indent=4)
        return True
    except OSError as error:
        print("Error: could not save artefact data. " + str(error))
        return False


def load_artefacts():
    """Load valid JSON data or start with an empty collection."""
    artefacts.clear()
    if not DATA_FILE.exists():
        return False

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
        if not isinstance(loaded, list):
            raise ValueError("saved data is not a list")

        required = {"id", "name", "category", "location", "condition",
                    "description", "acquisition_date"}
        for record in loaded:
            if not isinstance(record, dict) or not required.issubset(record):
                raise ValueError("saved data contains an invalid record")
            artefacts.append(record)
        return True
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print("Error: invalid or unreadable saved data. " + str(error))
        artefacts.clear()
        return False


def prompt_required(text):
    """Console-compatible required text prompt used by validation tests."""
    while True:
        value = input(text).strip()
        if value:
            return value
        print("Error: this field cannot be empty.")


def prompt_acquisition_date():
    """Return a valid DD-MM-YYYY date or an empty string."""
    while True:
        value = input("Acquisition Date (DD-MM-YYYY, optional): ").strip()
        if not value:
            return ""
        try:
            datetime.strptime(value, "%d-%m-%Y")
            return value
        except ValueError:
            print("Error: enter a valid date in DD-MM-YYYY format or leave it blank.")


def add_artefact():
    """Add an artefact from console input; retained for existing unit tests."""
    artefact_id = generate_artefact_id()
    name = prompt_required("Artefact Name: ")
    category = prompt_required("Artefact Category: ")
    location = prompt_required("Display Location: ")

    while True:
        condition = prompt_required("Artefact Condition: ").title()
        if validate_condition(condition):
            break
        print("Error: condition must be Good, Damaged, or Under Repair.")

    description = prompt_required("Description: ")
    acquisition_date = prompt_acquisition_date()
    record = {
        "id": artefact_id, "name": name, "category": category,
        "location": location, "condition": condition,
        "description": description, "acquisition_date": acquisition_date,
    }
    artefacts.append(record)
    save_artefacts()
    print("Success: Artefact " + artefact_id + " was added.")


def display_artefact(record):
    """Print one artefact in console-compatible detail format."""
    print("-" * 60)
    print("Artefact ID:       ", record["id"])
    print("Artefact Name:     ", record["name"])
    print("Category:          ", record["category"])
    print("Display Location:  ", record["location"])
    print("Condition:         ", record["condition"])
    print("Description:       ", record["description"])
    print("Acquisition Date:  ", record["acquisition_date"] or "Not recorded")
    print("-" * 60)


def update_condition():
    """Console-compatible condition update used by unit tests."""
    artefact_id = prompt_required("Enter Artefact ID: ").upper()
    record = find_artefact_by_id(artefact_id)
    if record is None:
        print("Error: no artefact was found with ID " + artefact_id + ".")
        return

    display_artefact(record)
    while True:
        selection = input("Select new condition (1-3): ").strip()
        if selection == "1":
            new_condition = "Good"
        elif selection == "2":
            new_condition = "Damaged"
        elif selection == "3":
            new_condition = "Under Repair"
        else:
            print("Error: enter a number from 1 to 3.")
            continue
        break

    record["condition"] = new_condition
    save_artefacts()
    print("Success: condition updated to " + new_condition + ".")


def view_all_artefacts():
    """Print all artefacts; retained for console-compatible unit tests."""
    print("\n--- View All Artefacts ---")
    if not artefacts:
        print("No artefacts have been registered.")
        return
    for record in artefacts:
        display_artefact(record)


def search_artefact():
    """Console-compatible repeated partial-name search."""
    print("\n--- Search Artefact ---")
    while True:
        search_text = input("Enter artefact name (or press Enter to return): ").strip()
        if not search_text:
            return
        matches = [record for record in artefacts
                   if search_text.lower() in record["name"].lower()]
        if not matches:
            print("No artefacts matched '" + search_text + "'.")
        else:
            print(str(len(matches)) + " matching artefact(s):")
            for record in matches:
                display_artefact(record)
        if input("Search again? (Y/N): ").strip().upper() != "Y":
            return


def delete_artefact():
    """Console-compatible confirmed deletion used by unit tests."""
    artefact_id = prompt_required("Enter Artefact ID: ").upper()
    record = find_artefact_by_id(artefact_id)
    if record is None:
        print("Error: no artefact was found with ID " + artefact_id + ".")
        return

    display_artefact(record)
    if input("Are you sure you want to delete this artefact? (Y/N): ").strip().upper() != "Y":
        print("Deletion cancelled. The artefact was not removed.")
        return
    artefacts.remove(record)
    save_artefacts()
    print("Success: Artefact " + artefact_id + " was deleted.")


def display_statistics():
    """Print collection totals and category counts."""
    print("\n--- Collection Statistics ---")
    print("Total artefacts:", len(artefacts))
    for condition in VALID_CONDITIONS:
        print(condition + ":",
              sum(1 for record in artefacts if record["condition"] == condition))

    categories = {}
    for record in artefacts:
        category = record["category"]
        categories[category] = categories.get(category, 0) + 1
    print("\nArtefacts by category:")
    if not categories:
        print("No categories registered.")
    else:
        for category, count in sorted(categories.items()):
            print(category + ": " + str(count))


class ArtefactGUI:
    """Tkinter interface for the artefact collection."""

    def __init__(self, root):
        self.root = root
        self.root.title("Artefact Management System")
        self.root.geometry("1180x720")
        self.root.minsize(980, 620)
        self.root.configure(bg="#F4F7FB")

        self.configure_styles()
        self.create_widgets()
        self.refresh_table()

    def configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("App.TFrame", background="#F4F7FB")
        style.configure("Card.TFrame", background="#FFFFFF", relief="flat")
        style.configure("Toolbar.TFrame", background="#FFFFFF")

        style.configure(
            "Title.TLabel",
            background="#17324D",
            foreground="#FFFFFF",
            font=("Segoe UI", 22, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background="#17324D",
            foreground="#C9D8E8",
            font=("Segoe UI", 10),
        )
        style.configure(
            "CardTitle.TLabel",
            background="#FFFFFF",
            foreground="#6B7C93",
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "CardValue.TLabel",
            background="#FFFFFF",
            foreground="#17324D",
            font=("Segoe UI", 20, "bold"),
        )
        style.configure(
            "Search.TLabel",
            background="#FFFFFF",
            foreground="#4A5D73",
            font=("Segoe UI", 10),
        )

        style.configure(
            "Primary.TButton",
            background="#2864A6",
            foreground="#FFFFFF",
            borderwidth=0,
            focusthickness=0,
            padding=(14, 9),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#1F527F"), ("pressed", "#173F61")],
            foreground=[("active", "#FFFFFF")],
        )
        style.configure(
            "Secondary.TButton",
            background="#EAF0F6",
            foreground="#17324D",
            borderwidth=0,
            padding=(13, 9),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#D8E4EF"), ("pressed", "#C7D7E7")],
        )
        style.configure(
            "Danger.TButton",
            background="#FBECEC",
            foreground="#A43A3A",
            borderwidth=0,
            padding=(13, 9),
            font=("Segoe UI", 9, "bold"),
        )
        style.map("Danger.TButton", background=[("active", "#F5DADA")])

        style.configure(
            "Search.TEntry",
            fieldbackground="#F8FAFC",
            borderwidth=1,
            relief="solid",
            padding=(10, 8),
        )
        style.configure(
            "Form.TCombobox",
            fieldbackground="#F8FAFC",
            background="#EAF0F6",
            foreground="#24384B",
            arrowcolor="#2864A6",
            bordercolor="#D6E0EA",
            lightcolor="#D6E0EA",
            darkcolor="#D6E0EA",
            padding=(8, 7),
        )
        style.map(
            "Form.TCombobox",
            fieldbackground=[("readonly", "#F8FAFC")],
            selectbackground=[("readonly", "#F8FAFC")],
            selectforeground=[("readonly", "#24384B")],
        )
        style.configure(
            "Modern.Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground="#2D3E50",
            borderwidth=0,
            rowheight=38,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Modern.Treeview.Heading",
            background="#EAF0F6",
            foreground="#17324D",
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padding=(8, 10),
        )
        style.map(
            "Modern.Treeview",
            background=[("selected", "#DCEAF7")],
            foreground=[("selected", "#17324D")],
        )
        style.map(
            "Modern.Treeview.Heading",
            background=[("active", "#DCE7F1")],
        )

        style.configure(
            "Status.TLabel",
            background="#F4F7FB",
            foreground="#60758B",
            font=("Segoe UI", 9),
            padding=(2, 5),
        )

    def create_widgets(self):
        header = tk.Frame(self.root, bg="#17324D", height=92)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_block = tk.Frame(header, bg="#17324D")
        title_block.pack(side="left", fill="both", expand=True, padx=24, pady=17)
        ttk.Label(title_block, text="Artefact Management",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_block, text="Local Heritage Community Collection",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))

        toolbar = ttk.Frame(self.root, style="Toolbar.TFrame")
        toolbar.pack(fill="x", padx=18, pady=(14, 10))

        ttk.Button(toolbar, text="+  Add Artefact", style="Primary.TButton",
                   command=self.open_add_dialog).pack(side="left", padx=(0, 7))
        ttk.Button(toolbar, text="Update Condition", style="Secondary.TButton",
                   command=self.update_selected_condition).pack(side="left", padx=7)
        ttk.Button(toolbar, text="Delete Artefact", style="Danger.TButton",
                   command=self.delete_selected).pack(side="left", padx=7)
        ttk.Button(toolbar, text="Statistics", style="Secondary.TButton",
                   command=self.show_statistics).pack(side="left", padx=7)

        search_frame = ttk.Frame(toolbar, style="Toolbar.TFrame")
        search_frame.pack(side="right")
        ttk.Label(search_frame, text="Search", style="Search.TLabel").pack(side="left", padx=(0, 8))
        self.search_entry = ttk.Entry(search_frame, width=25, style="Search.TEntry")
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", lambda event: self.search_gui())
        ttk.Button(search_frame, text="Find", style="Secondary.TButton",
                   command=self.search_gui).pack(side="left", padx=(7, 0))

        cards = ttk.Frame(self.root, style="App.TFrame")
        cards.pack(fill="x", padx=18, pady=(0, 10))
        card_specs = (
            ("total", "TOTAL ARTEFACTS", "0", "#2864A6"),
            ("good", "GOOD CONDITION", "0", "#2F8F68"),
            ("damaged", "DAMAGED", "0", "#C56A45"),
            ("repair", "UNDER REPAIR", "0", "#9A7C2F"),
        )
        self.card_values = {}
        for index, (key, label, value, accent) in enumerate(card_specs):
            card = ttk.Frame(cards, style="Card.TFrame")
            card.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 8, 8 if index == 3 else 0))
            cards.columnconfigure(index, weight=1)
            accent_line = tk.Frame(card, bg=accent, height=4)
            accent_line.pack(fill="x")
            body = tk.Frame(card, bg="#FFFFFF")
            body.pack(fill="x", padx=14, pady=(10, 11))
            ttk.Label(body, text=label, style="CardTitle.TLabel").pack(anchor="w")
            value_label = ttk.Label(body, text=value, style="CardValue.TLabel")
            value_label.pack(anchor="w", pady=(2, 0))
            self.card_values[key] = value_label

        table_container = ttk.Frame(self.root, style="App.TFrame")
        table_container.pack(fill="both", expand=True, padx=18, pady=(0, 8))

        table_frame = tk.Frame(table_container, bg="#FFFFFF", highlightbackground="#DDE6EF",
                               highlightthickness=1)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "name", "category", "location", "condition", "description", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                 style="Modern.Treeview")
        headings = {
            "id": "Artefact ID", "name": "Name", "category": "Category",
            "location": "Location", "condition": "Condition",
            "description": "Description", "date": "Acquisition Date",
        }
        widths = {"id": 95, "name": 180, "category": 120, "location": 150,
                  "condition": 110, "description": 260, "date": 130}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")

        vertical_scroll = ttk.Scrollbar(table_frame, orient="vertical",
                                        command=self.tree.yview)
        horizontal_scroll = ttk.Scrollbar(table_frame, orient="horizontal",
                                          command=self.tree.xview)
        self.tree.configure(yscrollcommand=vertical_scroll.set, xscrollcommand=horizontal_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree.tag_configure("even", background="#FFFFFF")
        self.tree.tag_configure("odd", background="#F7F9FC")
        self.tree.tag_configure("damaged", foreground="#A34E33")
        self.tree.tag_configure("repair", foreground="#806B25")

        self.status = ttk.Label(self.root, text="Ready", anchor="w",
                                style="Status.TLabel")
        self.status.pack(fill="x", padx=18, pady=(0, 8))

    def refresh_table(self, records=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        shown_records = artefacts if records is None else records
        for index, record in enumerate(shown_records):
            row_tag = "odd" if index % 2 else "even"
            tags = (row_tag,)
            if record["condition"] == "Damaged":
                tags += ("damaged",)
            elif record["condition"] == "Under Repair":
                tags += ("repair",)
            self.tree.insert("", "end", tags=tags, values=(
                record["id"], record["name"], record["category"], record["location"],
                record["condition"], record["description"],
                record["acquisition_date"] or "Not recorded",
            ))
        count_text = str(len(shown_records)) + " artefact(s) displayed"
        if len(shown_records) != len(artefacts):
            count_text += " from search"
        self.status.config(text="  " + count_text)

        self.card_values["total"].config(text=str(len(artefacts)))
        self.card_values["good"].config(text=str(
            sum(1 for record in artefacts if record["condition"] == "Good")))
        self.card_values["damaged"].config(text=str(
            sum(1 for record in artefacts if record["condition"] == "Damaged")))
        self.card_values["repair"].config(text=str(
            sum(1 for record in artefacts if record["condition"] == "Under Repair")))

    def open_add_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Artefact")
        dialog.resizable(False, False)
        dialog.configure(bg="#F4F7FB")
        dialog.geometry("600x470")
        dialog.transient(self.root)
        dialog.grab_set()

        header = tk.Frame(dialog, bg="#17324D", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="Add New Artefact", bg="#17324D", fg="#FFFFFF",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=22, pady=(12, 2))
        tk.Label(header, text="Register a historical collection item",
                 bg="#17324D", fg="#C9D8E8",
                 font=("Segoe UI", 9)).pack(anchor="w", padx=22)

        form = tk.Frame(dialog, bg="#FFFFFF", highlightbackground="#DDE6EF",
                        highlightthickness=1)
        form.pack(fill="both", expand=True, padx=18, pady=(16, 10))
        form.columnconfigure(1, weight=1)

        fields = (
            ("Name", ""),
            ("Category", ""),
            ("Display Location", ""),
            ("Description", ""),
            ("Acquisition Date (DD-MM-YYYY)", ""),
        )
        entries = {}
        for index, (label, _) in enumerate(fields):
            ttk.Label(form, text=label, background="#FFFFFF",
                      foreground="#4A5D73",
                      font=("Segoe UI", 9, "bold")).grid(
                row=index, column=0, sticky="w", padx=(18, 14), pady=7)
            entry = tk.Entry(
                form,
                font=("Segoe UI", 10),
                bg="#F8FAFC",
                fg="#24384B",
                insertbackground="#2864A6",
                relief="flat",
                highlightthickness=1,
                highlightbackground="#D6E0EA",
                highlightcolor="#2864A6",
            )
            entry.grid(row=index, column=1, sticky="ew", padx=(0, 18), pady=7, ipady=7)
            entries[label] = entry

        ttk.Label(form, text="Condition", background="#FFFFFF",
                  foreground="#4A5D73",
                  font=("Segoe UI", 9, "bold")).grid(
            row=5, column=0, sticky="w", padx=(18, 14), pady=7)
        condition_var = tk.StringVar(value="Good")
        condition_box = ttk.Combobox(
            form,
            textvariable=condition_var,
            values=VALID_CONDITIONS,
            state="readonly",
            style="Form.TCombobox",
        )
        condition_box.grid(row=5, column=1, sticky="ew", padx=(0, 18), pady=7, ipady=4)

        def submit():
            name = entries["Name"].get().strip()
            category = entries["Category"].get().strip()
            location = entries["Display Location"].get().strip()
            description = entries["Description"].get().strip()
            acquisition_date = entries["Acquisition Date (DD-MM-YYYY)"].get().strip()

            if not name or not category or not location or not description:
                messagebox.showerror("Validation Error",
                                     "Name, category, location and description cannot be empty.",
                                     parent=dialog)
                return
            if acquisition_date:
                try:
                    datetime.strptime(acquisition_date, "%d-%m-%Y")
                except ValueError:
                    messagebox.showerror("Validation Error",
                                         "Enter a valid DD-MM-YYYY date or leave it blank.",
                                         parent=dialog)
                    return

            record = {
                "id": generate_artefact_id(),
                "name": name, "category": category, "location": location,
                "condition": condition_var.get(), "description": description,
                "acquisition_date": acquisition_date,
            }
            artefacts.append(record)
            save_artefacts()
            dialog.destroy()
            self.refresh_table()
            messagebox.showinfo("Success", "Artefact " + record["id"] + " was added.",
                                parent=self.root)

        button_frame = tk.Frame(dialog, bg="#F4F7FB")
        button_frame.pack(fill="x", padx=18, pady=(0, 14))

        def make_dialog_button(parent, text, background, foreground, hover, command):
            button = tk.Button(
                parent,
                text=text,
                command=command,
                bg=background,
                fg=foreground,
                activebackground=hover,
                activeforeground=foreground,
                relief="flat",
                bd=0,
                padx=17,
                pady=9,
                cursor="hand2",
                font=("Segoe UI", 9, "bold"),
                takefocus=True,
            )
            button.bind("<Enter>", lambda event: button.config(bg=hover))
            button.bind("<Leave>", lambda event: button.config(bg=background))
            return button

        make_dialog_button(button_frame, "Add Artefact", "#2864A6", "#FFFFFF",
                           "#1F527F", submit).pack(side="right", padx=(8, 0))
        make_dialog_button(button_frame, "Cancel", "#EAF0F6", "#17324D",
                           "#D8E4EF", dialog.destroy).pack(side="right")
        entries["Name"].focus_set()

    def get_selected_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an artefact from the table.",
                                   parent=self.root)
            return None
        artefact_id = self.tree.item(selected[0], "values")[0]
        return find_artefact_by_id(artefact_id)

    def update_selected_condition(self):
        record = self.get_selected_record()
        if record is None:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Update Artefact Condition")
        dialog.resizable(False, False)
        dialog.configure(bg="#F4F7FB")
        dialog.geometry("480x330")
        dialog.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - 480) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - 330) // 2
        dialog.geometry("+{}+{}".format(x, y))
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.columnconfigure(0, weight=1)

        header = tk.Frame(dialog, bg="#17324D", height=82)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        tk.Label(header, text="Update Artefact Condition", bg="#17324D", fg="#FFFFFF",
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=24, pady=(16, 1))
        tk.Label(header, text=record["id"] + "  •  " + record["name"],
                 bg="#17324D", fg="#C9D8E8",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=24)

        content = tk.Frame(dialog, bg="#FFFFFF")
        content.grid(row=1, column=0, sticky="nsew", padx=18, pady=18)
        dialog.rowconfigure(1, weight=1)

        tk.Label(content, text="CURRENT CONDITION", bg="#FFFFFF", fg="#6B7C93",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=20, pady=(18, 5))
        tk.Label(content, text=record["condition"], bg="#FFFFFF", fg="#17324D",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20)

        tk.Label(content, text="NEW CONDITION", bg="#FFFFFF", fg="#6B7C93",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=20, pady=(17, 5))

        condition_var = tk.StringVar(value=record["condition"])
        ttk.Combobox(dialog, textvariable=condition_var, values=VALID_CONDITIONS,
                     state="readonly", width=44).place(
            x=38, y=215, width=404, height=32)

        def submit():
            record["condition"] = condition_var.get()
            save_artefacts()
            dialog.destroy()
            self.refresh_table()
            messagebox.showinfo("Success", "Condition updated to " + record["condition"] + ".",
                                parent=self.root)

        button_frame = tk.Frame(dialog, bg="#F4F7FB")
        button_frame.place(x=0, y=268, width=480, height=62)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        ttk.Button(button_frame, text="Cancel", style="Secondary.TButton",
                   command=dialog.destroy).grid(row=0, column=0, padx=(18, 7),
                                                pady=14, sticky="ew")
        ttk.Button(button_frame, text="Update Condition", style="Primary.TButton",
                   command=submit).grid(row=0, column=1, padx=(7, 18),
                                        pady=14, sticky="ew")

    def delete_selected(self):
        record = self.get_selected_record()
        if record is None:
            return
        confirmed = messagebox.askyesno(
            "Confirm Deletion",
            "Delete " + record["id"] + " - " + record["name"] + "?",
            parent=self.root,
        )
        if confirmed:
            artefacts.remove(record)
            save_artefacts()
            self.refresh_table()
            messagebox.showinfo("Deleted", "Artefact " + record["id"] + " was deleted.",
                                parent=self.root)

    def search_gui(self):
        search_text = self.search_entry.get().strip()
        if not search_text:
            self.refresh_table()
            return
        matches = [record for record in artefacts
                   if search_text.lower() in record["name"].lower()]
        self.refresh_table(matches)
        if not matches:
            messagebox.showinfo("Search Results",
                                "No artefacts matched '" + search_text + "'.",
                                parent=self.root)

    def show_statistics(self):
        good = sum(1 for record in artefacts if record["condition"] == "Good")
        damaged = sum(1 for record in artefacts if record["condition"] == "Damaged")
        under_repair = sum(1 for record in artefacts if record["condition"] == "Under Repair")

        categories = {}
        for record in artefacts:
            category = record["category"]
            categories[category] = categories.get(category, 0) + 1

        dialog = tk.Toplevel(self.root)
        dialog.title("Collection Statistics")
        dialog.resizable(False, False)
        dialog.configure(bg="#F4F7FB")
        dialog.geometry("520x430")
        dialog.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - 520) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - 430) // 2
        dialog.geometry("+{}+{}".format(x, y))
        dialog.transient(self.root)
        dialog.grab_set()

        header = tk.Frame(dialog, bg="#17324D", height=78)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="Collection Statistics", bg="#17324D", fg="#FFFFFF",
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=24, pady=(15, 1))
        tk.Label(header, text="Current collection overview", bg="#17324D", fg="#C9D8E8",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=24)

        cards = tk.Frame(dialog, bg="#F4F7FB")
        cards.pack(fill="x", padx=18, pady=(16, 10))
        card_data = (
            ("TOTAL", len(artefacts), "#2864A6"),
            ("GOOD", good, "#2F8F68"),
            ("DAMAGED", damaged, "#C56A45"),
            ("IN REPAIR", under_repair, "#9A7C2F"),
        )
        for index, (label, value, color) in enumerate(card_data):
            card = tk.Frame(cards, bg="#FFFFFF", highlightbackground="#DDE6EF",
                            highlightthickness=1)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 6, 6))
            cards.columnconfigure(index, weight=1)
            tk.Frame(card, bg=color, height=4).pack(fill="x")
            tk.Label(card, text=str(value), bg="#FFFFFF", fg="#17324D",
                     font=("Segoe UI", 18, "bold")).pack(pady=(10, 0))
            tk.Label(card, text=label, bg="#FFFFFF", fg="#6B7C93",
                     font=("Segoe UI", 8, "bold")).pack(pady=(1, 10))

        category_card = tk.Frame(dialog, bg="#FFFFFF", highlightbackground="#DDE6EF",
                                 highlightthickness=1)
        category_card.pack(fill="both", expand=True, padx=18, pady=(4, 12))
        tk.Label(category_card, text="ARTEFACTS BY CATEGORY", bg="#FFFFFF", fg="#6B7C93",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18, pady=(14, 8))

        if categories:
            for category, count in sorted(categories.items()):
                row = tk.Frame(category_card, bg="#FFFFFF")
                row.pack(fill="x", padx=18)
                tk.Label(row, text=category, bg="#FFFFFF", fg="#2D3E50",
                         font=("Segoe UI", 10)).pack(side="left", pady=5)
                tk.Label(row, text=str(count), bg="#EAF0F6", fg="#17324D",
                         width=5, font=("Segoe UI", 9, "bold")).pack(side="right", pady=5)
        else:
            tk.Label(category_card, text="No categories registered.",
                     bg="#FFFFFF", fg="#60758B",
                     font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=12)

        footer = tk.Frame(dialog, bg="#F4F7FB")
        footer.pack(fill="x")
        ttk.Button(footer, text="Close", style="Primary.TButton",
                   command=dialog.destroy).pack(side="right", padx=18, pady=12)


def main_menu():
    """Launch the Tkinter graphical main menu."""
    root = tk.Tk()

    if not DATA_FILE.exists():
        use_samples = messagebox.askyesnocancel(
            "Initial Collection",
            "Load 8 sample artefacts?\n\n"
            "Yes: load sample records\n"
            "No: start with an empty collection",
            parent=root,
        )
        if use_samples:
            artefacts.extend(
                {key: value for key, value in record.items()}
                for record in SAMPLE_ARTEFACTS
            )
        elif use_samples is None:
            root.destroy()
            return
        else:
            artefacts.clear()
        save_artefacts()
    else:
        load_artefacts()

    ArtefactGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main_menu()
