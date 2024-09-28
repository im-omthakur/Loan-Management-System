import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog, simpledialog
import sqlite3
import bcrypt 
import shutil
import os
from datetime import datetime
from tkcalendar import DateEntry

selected_file_paths = []
button_dict = {}

def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')

    # Create loans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            borrower_name TEXT,
            principal_amount REAL,
            monthly_interest_rate REAL,
            address TEXT,
            phone_number TEXT,
            emi_repayment_date DATE,
            documents TEXT
        )
    ''')

    # Create repayment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS repayment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER NOT NULL,  -- Foreign key referencing loans(id)
            payment_date DATE NOT NULL,  -- DATE type for payment date
            payment_amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE
        )
    ''')

    # Add a default user for testing
    hashed_password = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', ('admin', hashed_password))

    # Commit changes and close connection
    conn.commit()
    conn.close()

def login():
    username = entry_username.get()
    password = entry_password.get().encode('utf-8')
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password, user[0]):
        open_menu()
    else:
        # Do nothing on failed login
        pass

def change_password():
    username = entry_username.get()
    password = entry_password.get().encode('utf-8')
    new_password = entry_new_password.get().encode('utf-8')
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if user and bcrypt.checkpw(password, user[0]):
        hashed_new_password = bcrypt.hashpw(new_password, bcrypt.gensalt())
        cursor.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_new_password, username))
        conn.commit()
        messagebox.showinfo("Password Change", "Password updated successfully")
        reset_to_login()
    else:
        messagebox.showerror("Error", "Invalid username or password")
    
    conn.close()
    entry_new_password.delete(0, tk.END)

def reset_to_login():
    label_new_password.place_forget()
    entry_new_password.place_forget()
    button_change_password.place_forget()
    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)

def open_menu():
    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    root.geometry('800x600')  # Set a fixed size for the menu window

    label_menu = tk.Label(root, text="VAZIR FINANCE LTD", font=('Arial', 24, 'bold'))
    label_menu.pack(pady=20)

    button_add_loan = tk.Button(root, text="Add Loan Detail", command=open_add_loan_window, font=('Arial', 16))
    button_add_loan.pack(pady=10, fill=tk.X, padx=20)

    button_view_loans = tk.Button(root, text="View Existing Loan Details", command=view_loan_details, font=('Arial', 16))
    button_view_loans.pack(pady=10, fill=tk.X, padx=20)

def upload_file():
    global selected_file_paths
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        # Define the destination directory
        os.makedirs("documents", exist_ok=True)
        selected_file_paths = []
        for file_path in file_paths:
            # Define the destination path
            file_name = os.path.basename(file_path)
            destination_path = os.path.join("documents", file_name)
            
            # Copy the selected file to the destination directory
            shutil.copy(file_path, destination_path)
            selected_file_paths.append(destination_path)
            print(f"File uploaded and stored at: {destination_path}")

def open_add_loan_window():
    add_loan_window = tk.Toplevel(root)
    add_loan_window.title("Add Loan Detail")
    add_loan_window.geometry('500x600')

    label_add_loan = tk.Label(add_loan_window, text="Add Loan Detail", font=('Arial', 24, 'bold'))
    label_add_loan.pack(pady=20)

    tk.Label(add_loan_window, text="Borrower Name", font=('Arial', 14)).pack(pady=5)
    entry_borrower_name = tk.Entry(add_loan_window, font=('Arial', 14))
    entry_borrower_name.pack(pady=5)

    tk.Label(add_loan_window, text="Principal Amount", font=('Arial', 14)).pack(pady=5)
    entry_principal_amount = tk.Entry(add_loan_window, font=('Arial', 14))
    entry_principal_amount.pack(pady=5)

    tk.Label(add_loan_window, text="Monthly Interest Rate (%)", font=('Arial', 14)).pack(pady=5)
    entry_monthly_interest_rate = tk.Entry(add_loan_window, font=('Arial', 14))
    entry_monthly_interest_rate.pack(pady=5)

    tk.Label(add_loan_window, text="Address", font=('Arial', 14)).pack(pady=5)
    entry_address = tk.Entry(add_loan_window, font=('Arial', 14))
    entry_address.pack(pady=5)

    tk.Label(add_loan_window, text="Phone Number", font=('Arial', 14)).pack(pady=5)
    entry_phone_number = tk.Entry(add_loan_window, font=('Arial', 14))
    entry_phone_number.pack(pady=5)

    tk.Label(add_loan_window, text="EMI Repayment Date", font=('Arial', 14)).pack(pady=5)
    entry_emi_repayment_date = DateEntry(add_loan_window, font=('Arial', 14))
    entry_emi_repayment_date.pack(pady=5)

    tk.Label(add_loan_window, text="Document Upload", font=('Arial', 14)).pack(pady=5)
    button_document_upload = tk.Button(add_loan_window, text="Choose Files", font=('Arial', 14), command=upload_file)
    button_document_upload.pack(pady=5)

    tk.Button(add_loan_window, text="Add Borrower", font=('Arial', 14), command=lambda: save_loan_details(
        entry_borrower_name.get(),
        entry_principal_amount.get(),
        entry_monthly_interest_rate.get(),
        entry_address.get(),
        entry_phone_number.get(),
        entry_emi_repayment_date.get_date(),
        selected_file_paths,
        add_loan_window
    )).pack(pady=20)

def save_loan_details(borrower_name, principal_amount, monthly_interest_rate, address, phone_number, emi_repayment_date, documents, add_loan_window):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    documents_str = ','.join(documents)
    cursor.execute('''
        INSERT INTO loans (borrower_name, principal_amount, monthly_interest_rate, address, phone_number, emi_repayment_date, documents)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (borrower_name, principal_amount, monthly_interest_rate, address, phone_number, emi_repayment_date, documents_str))
    conn.commit()
    conn.close()
    messagebox.showinfo("Add Borrower", "Details submitted!")
    add_loan_window.destroy()

def on_search(event=None):
    """Function to search for loans based on the query."""
    query = search_entry.get()
    if query != 'Search By Name':
        search_loans(query, tree)

def search_loans(query, search_date, tree):
    # Clear existing rows
    for item in tree.get_children():
        tree.delete(item)

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # If query still has the placeholder, treat it as empty
    if query == 'Search By Name':
        query = ''

    # Format date for comparison
    search_date_str = search_date.strftime('%Y-%m-%d') if search_date else None
    print(f"Search Name: {query}, Search Date: {search_date_str}")

    # Search by both name and date, or just name or date
    if query and search_date_str:
        cursor.execute("SELECT * FROM loans WHERE borrower_name LIKE ? AND emi_repayment_date = ?", 
                       ('%' + query + '%', search_date_str))
    elif query:
        cursor.execute("SELECT * FROM loans WHERE borrower_name LIKE ?", ('%' + query + '%',))
    elif search_date_str:
        cursor.execute("SELECT * FROM loans WHERE emi_repayment_date = ?", (search_date_str,))
    else:
        cursor.execute("SELECT * FROM loans")

    loans = cursor.fetchall()
    conn.close()

    print(f"Fetched Loans: {loans}")  # Debugging print statement

    # Insert data into the Treeview
    for loan in loans:
        tree.insert('', 'end', values=loan)

def on_entry_click(event):
    """Function to handle placeholder text in search bar."""
    if search_entry.get() == 'Search By Name':
        search_entry.delete(0, 'end')  # delete all the text in the entry
        search_entry.insert(0, '')  # insert blank for user input
        search_entry.config(fg='black')

def on_focusout(event):
    """Function to handle re-adding placeholder text if entry is empty."""
    if search_entry.get() == '':
        search_entry.insert(0, 'Search By Name')
        search_entry.config(fg='grey')

def open_documents(document_paths):
    """Function to open documents."""
    for path in document_paths:
        view_file(path)

def view_file(file_path):
    """Function to open or preview the file."""
    if os.path.exists(file_path):
        os.startfile(file_path)  # Windows: Opens the file with the default application
        # On macOS or Linux, use: webbrowser.open(file_path)
    else:
        messagebox.showerror("Error", "No Documents Were Added For This Borrower.")

def sort_treeview(tree, column, reverse):
    """Sort the Treeview based on the selected column."""
    data = [(tree.item(item)['values'], item) for item in tree.get_children('')]
    data.sort(key=lambda x: x[0][column], reverse=reverse)
    for index, (values, item) in enumerate(data):
        tree.move(item, '', index)
    tree.heading(column, command=lambda col=column: sort_treeview(tree, col, not reverse))

def on_treeview_click(event):
    """Function to handle clicks on the Treeview."""
    item = tree.identify_row(event.y)
    column = tree.identify_column(event.x)
    
    if item:  # Ensure an item is clicked
        documents = tree.item(item, 'values')[7]

        # Remove existing buttons if they exist
        for btn in button_dict.values():
            btn.destroy()
        
        # Initialize button_dict to store new buttons
        button_dict.clear()

        # Create additional buttons
        button_names = [
            "Show Documents",
            "Update Loan Record",
            "Delete Loan Record",
            "Record A Payment",
            "Show Payment History"
        ]
        button_commands = [
            lambda: open_documents(documents.split(',')),
            lambda: update_loan(item),
            lambda: delete_loan(item),
            lambda: record_payment(item),
            lambda: show_payment_history(item)
        ]
        
        # Get the width and height of the view_window
        window_width = view_window.winfo_width()
        button_width = 150  # Width of each button
        num_buttons = len(button_names)
        
        # Calculate total width for buttons and spacing
        total_button_width = button_width * num_buttons
        total_spacing = window_width - total_button_width - 40  # 20 padding on each side
        spacing = total_spacing / (num_buttons + 1)  # Space between buttons
        
        # Common y position for all buttons (bottom-right)
        y_position = view_window.winfo_height() - 50  # Adjust for padding from bottom

        for i, (name, command) in enumerate(zip(button_names, button_commands)):
            button_dict[name] = tk.Button(
                view_window, 
                text=name, 
                font=('Arial', 12), 
                command=command
            )
            
            # Calculate x position for each button
            x_position = spacing * (i + 1) + button_width * i
            button_dict[name].place(x=x_position, y=y_position)

def update_loan(item):
    """Function to update loan record."""
    loan_id = tree.item(item, 'values')[0]
    # Implement the logic to update the loan record
    messagebox.showinfo("Update", f"Update Loan Record for Loan ID: {loan_id}")

def delete_loan(item):
    """Function to delete loan record."""
    # Get the loan_id from the selected item in the Treeview
    loan_id = tree.item(item, 'values')[0]

    # Ask the user for confirmation before deletion
    confirm = messagebox.askyesno("Delete Confirmation", f"Are you sure you want to delete Loan ID: {loan_id}?")

    if confirm:
        try:
            # Connect to the database
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            # Replace loan_id with the actual primary key column name (e.g., id)
            cursor.execute('DELETE FROM loans WHERE id = ?', (loan_id,))

            # Commit the changes to the database
            conn.commit()

            # Close the connection
            conn.close()

            # Remove the loan from the Treeview
            tree.delete(item)

            # Show success message
            messagebox.showinfo("Success", f"Loan ID: {loan_id} has been successfully deleted.")

        except Exception as e:
            # Handle any errors that occur
            messagebox.showerror("Error", f"Failed to delete Loan ID: {loan_id}. Error: {str(e)}")
    else:
        # User cancelled the deletion
        messagebox.showinfo("Cancelled", "Loan deletion cancelled.")

def record_payment(item):
    """Function to record a payment with a form for input."""

    # Retrieve loan_id from the selected item in the treeview
    loan_id = tree.item(item, 'values')[0]

    # Create a new Toplevel window for the form
    form_window = tk.Toplevel()
    form_window.title(f"Record Payment for Loan ID: {loan_id}")

    # Function to handle form submission
    def submit_payment():
        payment_date = payment_date_entry.get()
        payment_amount = payment_amount_entry.get()
        payment_method = payment_method_entry.get()
        notes = notes_entry.get()

        # Validate required fields
        if not payment_date or not payment_amount or not payment_method:
            messagebox.showwarning("Input Error", "Please fill in all required fields (date, amount, method).", parent=form_window)
            return

        try:
            # Convert payment amount to float
            payment_amount_float = float(payment_amount)

            # Validate and parse the date format
            payment_date_obj = datetime.strptime(payment_date, "%Y-%m-%d").date()

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid data: {str(e)}", parent=form_window)
            return

        # Record the payment in the repayment table
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            # Insert the payment details into the repayment table
            cursor.execute('''
                INSERT INTO repayment (loan_id, payment_date, payment_amount, payment_method, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (loan_id, payment_date, payment_amount_float, payment_method, notes))

            conn.commit()
            conn.close()

            # Inform the user that the payment was recorded successfully
            messagebox.showinfo("Success", f"Payment of {payment_amount_float} recorded for Loan ID: {loan_id}", parent=form_window)

            # Close the form window after successful submission
            form_window.destroy()

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred while recording the payment: {str(e)}", parent=form_window)

    # Create labels and entries for payment details
    tk.Label(form_window, text="Payment Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=5, sticky='w')
    payment_date_entry = tk.Entry(form_window)
    payment_date_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(form_window, text="Payment Amount:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
    payment_amount_entry = tk.Entry(form_window)
    payment_amount_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(form_window, text="Payment Method:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
    payment_method_entry = tk.Entry(form_window)
    payment_method_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(form_window, text="Notes (optional):").grid(row=3, column=0, padx=10, pady=5, sticky='w')
    notes_entry = tk.Entry(form_window)
    notes_entry.grid(row=3, column=1, padx=10, pady=5)

    # Add submit button
    submit_button = tk.Button(form_window, text="Submit Payment", command=submit_payment)
    submit_button.grid(row=4, column=0, columnspan=2, pady=10)

    # Run the window loop
    form_window.mainloop()

def show_payment_history(item):
    """Function to show payment history."""
    loan_id = tree.item(item, 'values')[0]
    
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Fetch repayment history for the selected loan
    cursor.execute('''
        SELECT payment_date, payment_amount, payment_method, notes 
        FROM repayment 
        WHERE loan_id = ?
        ORDER BY payment_date ASC
    ''', (loan_id,))
    
    # Fetch all repayment records for the loan
    payments = cursor.fetchall()
    
    # Close the connection
    conn.close()
    
    # If there are no payments, show a message
    if not payments:
        messagebox.showinfo("Payment History", f"No payment history found for Loan ID: {loan_id}")
        return
    
    # Format the payment history for display
    payment_history = f"Payment History for Loan ID: {loan_id}\n\n"
    for payment in payments:
        payment_date, payment_amount, payment_method, notes = payment
        payment_history += f"Date: {payment_date}\nAmount: {payment_amount}\nMethod: {payment_method}\nNotes: {notes if notes else 'N/A'}\n\n"
    
    # Display the payment history in a messagebox
    messagebox.showinfo("Payment History", payment_history)

def view_loan_details():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM loans')
    loans = cursor.fetchall()
    conn.close()

    global view_window
    view_window = tk.Toplevel(root)
    view_window.title("View Loan Details")
    view_window.geometry('900x500')  # Increased width for better space

    # Frame for search bar
    search_frame = tk.Frame(view_window)
    search_frame.pack(fill='x', pady=10, padx=10)

    # Search Entry for borrower name (leftmost)
    global search_entry
    search_entry = tk.Entry(search_frame, font=('Arial', 12), width=30)
    search_entry.insert(0, 'Search By Name')
    search_entry.bind('<FocusIn>', on_entry_click)
    search_entry.bind('<FocusOut>', on_focusout)
    search_entry.config(fg='grey')
    search_entry.pack(side='left', fill='x', expand=True, padx=(5, 10))

    # DateEntry for EMI repayment date (shifted left)
    date_label = tk.Label(search_frame, text="Search by EMI Date:", font=('Arial', 12))
    date_label.pack(side='left', padx=(0, 5))

    date_entry = DateEntry(search_frame, font=('Arial', 12), width=12, date_pattern='yyyy-mm-dd', 
                           selectmode='day', mindate=None, maxdate=None)
    date_entry.pack(side='left', padx=(0, 10))

    # Search button
    search_button = tk.Button(search_frame, text="Search", font=('Arial', 12), 
                              command=lambda: search_loans(search_entry.get(), date_entry.get_date(), tree))
    search_button.pack(side='left', padx=(0, 10))

    # Reset button
    reset_button = tk.Button(search_frame, text="Show All Records", font=('Arial', 12), 
                             command=show_all_records)
    reset_button.pack(side='left', padx=(0, 10))

    # Frame for Treeview and Scrollbar
    tree_frame = tk.Frame(view_window)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Create the Treeview widget
    global tree
    tree = ttk.Treeview(tree_frame, columns=('loan_id', 'borrower_name', 'principal_amount', 
                                             'monthly_interest_rate', 'address', 'phone_number', 
                                             'emi_repayment_date', 'documents'), show='headings')
    
    # Define headings with sorting capabilities
    tree.heading('loan_id', text='Loan ID', command=lambda: sort_treeview(tree, 0, False))
    tree.heading('borrower_name', text='Borrower Name', command=lambda: sort_treeview(tree, 1, False))
    tree.heading('principal_amount', text='Principal Amount', command=lambda: sort_treeview(tree, 2, False))
    tree.heading('monthly_interest_rate', text='Monthly Interest Rate', command=lambda: sort_treeview(tree, 3, False))
    tree.heading('address', text='Address', command=lambda: sort_treeview(tree, 4, False))
    tree.heading('phone_number', text='Phone Number', command=lambda: sort_treeview(tree, 5, False))
    tree.heading('emi_repayment_date', text='EMI Repayment Date', command=lambda: sort_treeview(tree, 6, False))
    tree.heading('documents', text='Documents', command=lambda: sort_treeview(tree, 7, False))

    # Set column widths
    tree.column('loan_id', width=50)
    tree.column('borrower_name', width=150)
    tree.column('principal_amount', width=100)
    tree.column('monthly_interest_rate', width=120)
    tree.column('address', width=200)
    tree.column('phone_number', width=120)
    tree.column('emi_repayment_date', width=120)
    tree.column('documents', width=200)

    # Insert data into the Treeview
    for loan in loans:
        tree.insert('', 'end', values=loan)

    # Create a vertical scrollbar
    scrollbar = tk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Pack Treeview and Scrollbar
    tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    # Bottom Frame for fixed buttons
    button_frame = tk.Frame(view_window)
    button_frame.pack(side='bottom', pady=10)

    # Create and place buttons
    button_names = [
        "Show Documents", "Update Loan Record", "Delete Loan Record", 
        "Record A Payment", "Show Payment History"
    ]
    button_commands = [
        lambda: open_documents(tree.item(tree.selection()[0], 'values')[7].split(',')),
        lambda: update_loan(tree.selection()[0]),
        lambda: delete_loan(tree.selection()[0]),
        lambda: record_payment(tree.selection()[0]),
        lambda: show_payment_history(tree.selection()[0])
    ]

    for name, command in zip(button_names, button_commands):
        button = tk.Button(button_frame, text=name, font=('Arial', 12), command=command)
        button.pack(side='left', padx=5)

def show_all_records():
    # Function to show all records in the Treeview
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM loans')
    loans = cursor.fetchall()
    conn.close()

    tree.delete(*tree.get_children())  # Clear existing rows

    for loan in loans:
        tree.insert('', 'end', values=loan)

def on_resize(event):
    root.config(bg='#1E90FF')  # Set background color to blue

setup_database()

root = tk.Tk()
root.title("Login Screen")

window_width = 800
window_height = 600  

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)

root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

root.config(bg='#1E90FF')

frame = tk.Frame(root, bg='#ffffff', bd=2, relief='solid', highlightbackground='#000000', highlightthickness=1)
frame.place(relx=0.75, rely=0.5, anchor='center', width=400, height=400)

title_text = "VAZIR FINANCE\nLTD"
label_title = tk.Label(root, text=title_text, bg='#1E90FF', fg='#ffffff', font=('Arial', 24, 'bold'))
label_title.place(relx=0.25, rely=0.5, anchor='center')

label_signin = tk.Label(frame, text="Sign In", bg='#ffffff', fg='#000000', font=('Arial', 20, 'bold'))
label_signin.place(relx=0.5, rely=0.2, anchor='center')

entry_username = tk.Entry(frame, font=('Arial', 16), bd=2, relief='groove', bg='#ffffff', fg='#000000', insertbackground='black')
entry_username.place(relx=0.5, rely=0.35, anchor='center', width=350)  
entry_username.insert(0, "Username")
entry_username.bind("<FocusIn>", lambda e: on_entry_focus_in(e, "Username"))
entry_username.bind("<FocusOut>", lambda e: on_entry_focus_out(e, "Username"))


entry_password = tk.Entry(frame, show='', font=('Arial', 16), bd=2, relief='groove', bg='#ffffff', fg='#000000', insertbackground='black')
entry_password.place(relx=0.5, rely=0.45, anchor='center', width=350)  
entry_password.insert(0, "Password")
entry_password.bind("<FocusIn>", lambda e: on_entry_focus_in(e, "Password"))
entry_password.bind("<FocusOut>", lambda e: on_entry_focus_out(e, "Password"))

label_new_password = tk.Label(frame, text="New Password", bg='#ffffff', fg='#000000', font=('Arial', 16))
label_new_password.place(relx=0.5, rely=0.6, anchor='center')  
entry_new_password = tk.Entry(frame, show='*', font=('Arial', 16), bd=2, relief='groove', bg='#ffffff', fg='#000000', insertbackground='black')
entry_new_password.place(relx=0.5, rely=0.65, anchor='center', width=250)  
label_new_password.place_forget()
entry_new_password.place_forget()

button_login = tk.Button(frame, text="Login", command=login, bg='#4CAF50', fg='#ffffff', font=('Arial', 16), relief='flat')
button_login.place(relx=0.5, rely=0.58, anchor='center', width=120, height=30) 


def show_change_password():
    label_new_password.place(relx=0.5, rely=0.75, anchor='center')  # Adjusted position
    entry_new_password.place(relx=0.5, rely=0.82, anchor='center', width=250)  # Adjusted position and width
    button_change_password.place(relx=0.5, rely=0.9, anchor='center', width=300, height=30)  # Adjusted vertical position

button_show_change_password = tk.Button(frame, text="Change Password", command=show_change_password, bg='#FF9800', fg='#ffffff', font=('Arial', 16), relief='flat')
button_show_change_password.place(relx=0.5, rely=0.69, anchor='center', width=200, height=30)  

button_change_password = tk.Button(frame, text="Submit New Password", command=change_password, bg='#2196F3', fg='#ffffff', font=('Arial', 14), relief='flat')
button_change_password.place(relx=0.5, rely=0.9, anchor='center', width=300, height=30)  
button_change_password.place_forget()

def on_entry_focus_in(event, placeholder):
    if event.widget.get() == placeholder:
        event.widget.delete(0, tk.END)
        event.widget.config(fg='#000000')  
        if event.widget == entry_password:
            event.widget.config(show='*')  

def on_entry_focus_out(event, placeholder):
    if event.widget.get() == '':
        event.widget.insert(0, placeholder)
        event.widget.config(fg='#A9A9A9')  
        if event.widget == entry_password:
            event.widget.config(show='')  

root.bind('<Return>', lambda event: login())

root.bind("<Configure>", on_resize)

root.mainloop()