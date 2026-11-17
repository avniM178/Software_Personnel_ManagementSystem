import customtkinter as ctk
from tkinter import ttk, messagebox
from database import create_connection

BG="#F3F5F8"; WHITE="#FFFFFF"; NAVY="#17243A"
TEAL="#168C89"; TEXT="#202C3D"; MUTED="#8490A0"; BORDER="#E4E9EF"

class DataManagerFrame(ctk.CTkFrame):
    """Schema-aware MySQL CRUD interface for the SPMS tables."""
    def __init__(self,master,table,title):
        super().__init__(master,fg_color=BG,corner_radius=0)
        self.table=table; self.title_text=title
        self.columns=[]; self.info={}; self.inputs={}; self.pk=None
        self.selected_pk=None
        self.pack(fill="both",expand=True)
        self._build()
        self._schema()
        self.load_rows()

    def _conn(self):
        c=create_connection()
        if c is None: raise ConnectionError("MySQL connection failed. Check config.py.")
        return c

    def _build(self):
        self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(2,weight=1)
        ctk.CTkLabel(self,text=f"{self.title_text} Management",text_color=TEXT,
            font=ctk.CTkFont(size=24,weight="bold")).grid(
                row=0,column=0,sticky="w",pady=(2,3))
        ctk.CTkLabel(self,text="Create, view, search, update and delete database records.",
            text_color=MUTED).grid(row=1,column=0,sticky="w",pady=(0,13))
        body=ctk.CTkFrame(self,fg_color="transparent")
        body.grid(row=2,column=0,sticky="nsew")
        body.grid_columnconfigure(1,weight=1); body.grid_rowconfigure(0,weight=1)

        self.form=ctk.CTkScrollableFrame(body,width=265,fg_color=WHITE,
            corner_radius=12,border_width=1,border_color=BORDER)
        self.form.grid(row=0,column=0,sticky="ns",padx=(0,12))
        ctk.CTkLabel(self.form,text="Record details",text_color=TEXT,
            font=ctk.CTkFont(size=16,weight="bold")).pack(
                anchor="w",padx=12,pady=(12,8))
        self.fields=ctk.CTkFrame(self.form,fg_color="transparent")
        self.fields.pack(fill="x",padx=9)
        buttons=ctk.CTkFrame(self.form,fg_color="transparent")
        buttons.pack(fill="x",padx=9,pady=12)
        for text,color,cmd in [
            ("Add record",TEAL,self.add_record),
            ("Update selected",NAVY,self.update_record),
            ("Delete selected","#B94B55",self.delete_record),
            ("Clear form","#E9EEF3",self.clear_form)]:
            ctk.CTkButton(buttons,text=text,fg_color=color,
                hover_color="#DCE4EC" if color=="#E9EEF3" else color,
                text_color=NAVY if color=="#E9EEF3" else WHITE,
                command=cmd).pack(fill="x",pady=3)

        right=ctk.CTkFrame(body,fg_color=WHITE,corner_radius=12,
            border_width=1,border_color=BORDER)
        right.grid(row=0,column=1,sticky="nsew")
        right.grid_columnconfigure(0,weight=1); right.grid_rowconfigure(1,weight=1)
        bar=ctk.CTkFrame(right,fg_color="transparent")
        bar.grid(row=0,column=0,sticky="ew",padx=10,pady=10)
        bar.grid_columnconfigure(0,weight=1)
        self.search=ctk.CTkEntry(bar,placeholder_text="Search any field...",height=36)
        self.search.grid(row=0,column=0,sticky="ew")
        self.search.bind("<Return>",lambda e:self.load_rows())
        ctk.CTkButton(bar,text="Search",width=78,fg_color=TEAL,
            command=self.load_rows).grid(row=0,column=1,padx=5)
        ctk.CTkButton(bar,text="Refresh",width=78,fg_color=NAVY,
            command=self.refresh).grid(row=0,column=2)
        wrap=ctk.CTkFrame(right,fg_color=WHITE)
        wrap.grid(row=1,column=0,sticky="nsew",padx=9,pady=(0,8))
        wrap.grid_columnconfigure(0,weight=1); wrap.grid_rowconfigure(0,weight=1)
        self.tree=ttk.Treeview(wrap,show="headings",selectmode="browse")
        self.tree.grid(row=0,column=0,sticky="nsew")
        sy=ttk.Scrollbar(wrap,orient="vertical",command=self.tree.yview)
        sy.grid(row=0,column=1,sticky="ns")
        sx=ttk.Scrollbar(wrap,orient="horizontal",command=self.tree.xview)
        sx.grid(row=1,column=0,sticky="ew")
        self.tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
        self.tree.bind("<<TreeviewSelect>>",self.select_row)
        self.status=ctk.CTkLabel(right,text="",text_color=MUTED)
        self.status.grid(row=2,column=0,sticky="w",padx=12,pady=(0,8))

    def _schema(self):
        conn=cur=None
        try:
            conn=self._conn(); cur=conn.cursor()
            cur.execute(f"SHOW COLUMNS FROM `{self.table}`")
            rows=cur.fetchall()
            if not rows: raise RuntimeError(f"Table {self.table} has no columns.")
            self.columns=[r[0] for r in rows]
            self.info={r[0]:{"type":str(r[1]).lower(),"null":r[2]=="YES",
                "key":r[3],"default":r[4],"extra":str(r[5]).lower()} for r in rows}
            pks=[r[0] for r in rows if r[3]=="PRI"]
            self.pk=pks[0] if pks else self.columns[0]
            self.tree["columns"]=self.columns
            for col in self.columns:
                self.tree.heading(col,text=col.replace("_"," ").upper())
                self.tree.column(col,width=145,minwidth=85,stretch=True)
            self._make_inputs()
        except Exception as e: messagebox.showerror("Table schema error",str(e))
        finally:
            if cur: cur.close()
            if conn: conn.close()

    def _make_inputs(self):
        for w in self.fields.winfo_children(): w.destroy()
        self.inputs={}
        for col in self.columns:
            inf=self.info[col]
            if "auto_increment" in inf["extra"]: continue
            if col=="created_at" and inf["default"] is not None: continue
            ctk.CTkLabel(self.fields,text=col.replace("_"," ").upper(),
                text_color=TEXT,font=ctk.CTkFont(size=9,weight="bold")
                ).pack(anchor="w",pady=(7,2))
            typ=inf["type"]
            if typ.startswith("enum("):
                vals=typ[5:-1].replace("'","").split(",")
                widget=ctk.CTkOptionMenu(self.fields,values=vals)
                if vals: widget.set(vals[0])
            else:
                hint="YYYY-MM-DD" if typ=="date" else f"Enter {col.replace('_',' ')}"
                widget=ctk.CTkEntry(self.fields,height=34,placeholder_text=hint)
            widget.pack(fill="x")
            self.inputs[col]=widget

    def _collect(self):
        data={}
        for col,w in self.inputs.items():
            value=w.get().strip(); inf=self.info[col]; typ=inf["type"]
            if not value:
                if not inf["null"] and inf["default"] is None:
                    raise ValueError(f"{col.replace('_',' ').title()} is required.")
                data[col]=None; continue
            if typ.startswith(("int","bigint","smallint","tinyint")):
                try: data[col]=int(value)
                except ValueError: raise ValueError(f"{col} must be a whole number.")
            elif typ.startswith(("decimal","float","double")):
                try: data[col]=float(value)
                except ValueError: raise ValueError(f"{col} must be numeric.")
            else: data[col]=value
        return data

    def load_rows(self):
        conn=cur=None
        try:
            conn=self._conn(); cur=conn.cursor()
            term=self.search.get().strip()
            sql=f"SELECT * FROM `{self.table}`"; params=()
            if term:
                cols=[c for c in self.columns if not self.info[c]["type"].startswith(
                    ("blob","binary","varbinary"))]
                if cols:
                    sql+=" WHERE "+" OR ".join(
                        f"CAST(`{c}` AS CHAR) LIKE %s" for c in cols)
                    params=tuple([f"%{term}%"]*len(cols))
            sql+=f" ORDER BY `{self.pk}` DESC"
            cur.execute(sql,params); rows=cur.fetchall()
            self.tree.delete(*self.tree.get_children())
            for row in rows:
                self.tree.insert("", "end",values=[
                    "" if v is None else str(v) for v in row])
            self.status.configure(text=f"{len(rows)} record(s)")
        except Exception as e: messagebox.showerror("Load records error",str(e))
        finally:
            if cur: cur.close()
            if conn: conn.close()

    def select_row(self,event=None):
        selected=self.tree.selection()
        if not selected:return
        values=self.tree.item(selected[0],"values")
        record=dict(zip(self.columns,values))
        self.selected_pk=record.get(self.pk)
        for col,w in self.inputs.items():
            val=record.get(col,"")
            if isinstance(w,ctk.CTkOptionMenu):
                if val: w.set(val)
            else:
                w.delete(0,"end")
                if val: w.insert(0,val)

    def add_record(self):
        conn=cur=None
        try:
            data=self._collect()
            cols=list(data)
            if not cols: raise ValueError("No editable fields in this table.")
            conn=self._conn(); cur=conn.cursor()
            names=", ".join(f"`{c}`" for c in cols)
            marks=", ".join(["%s"]*len(cols))
            cur.execute(f"INSERT INTO `{self.table}` ({names}) VALUES ({marks})",
                        tuple(data[c] for c in cols))
            conn.commit(); messagebox.showinfo("Saved","Record added successfully.")
            self.clear_form(); self.load_rows()
        except Exception as e:
            if conn: conn.rollback()
            messagebox.showerror("Add record error",str(e))
        finally:
            if cur: cur.close()
            if conn: conn.close()

    def update_record(self):
        if self.selected_pk is None:
            messagebox.showwarning("Select record","Select a row to update."); return
        conn=cur=None
        try:
            data=self._collect(); cols=list(data)
            if not cols: raise ValueError("No editable fields.")
            sets=", ".join(f"`{c}`=%s" for c in cols)
            conn=self._conn(); cur=conn.cursor()
            cur.execute(f"UPDATE `{self.table}` SET {sets} WHERE `{self.pk}`=%s",
                        tuple(data[c] for c in cols)+(self.selected_pk,))
            conn.commit(); messagebox.showinfo("Updated","Record updated.")
            self.clear_form(); self.load_rows()
        except Exception as e:
            if conn: conn.rollback()
            messagebox.showerror("Update error",str(e))
        finally:
            if cur: cur.close()
            if conn: conn.close()

    def delete_record(self):
        if self.selected_pk is None:
            messagebox.showwarning("Select record","Select a row to delete."); return
        if not messagebox.askyesno("Confirm delete",
                "Permanently delete this record? Related records may prevent deletion."):
            return
        conn=cur=None
        try:
            conn=self._conn(); cur=conn.cursor()
            cur.execute(f"DELETE FROM `{self.table}` WHERE `{self.pk}`=%s",
                        (self.selected_pk,))
            conn.commit(); messagebox.showinfo("Deleted","Record deleted.")
            self.clear_form(); self.load_rows()
        except Exception as e:
            if conn: conn.rollback()
            messagebox.showerror("Delete error",str(e))
        finally:
            if cur: cur.close()
            if conn: conn.close()

    def clear_form(self):
        for col,w in self.inputs.items():
            if isinstance(w,ctk.CTkOptionMenu):
                vals=w.cget("values")
                if vals:w.set(vals[0])
            else:w.delete(0,"end")
        self.selected_pk=None
        for item in self.tree.selection():self.tree.selection_remove(item)

    def refresh(self):
        self.search.delete(0,"end")
        self.load_rows()
