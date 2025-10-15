import tkinter
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import customtkinter
import main as pcc


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # ======== Configuration de la fenêtre principale ========
        self.title("Volatile : Détecteur de passes")
        self.geometry("1100x580")
        self.minsize(900, 500)

        # Mode d'apparence et thème
        customtkinter.set_appearance_mode("System")  # "System", "Dark", "Light"
        customtkinter.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

        # ======== Layout principal ========
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ======== Barre latérale ========
        self.sidebar_frame = customtkinter.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Menu Principal",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text='🎥 Choisir une vidéo', command=self.choixvideo)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text='📡 Mode Direct', command=self.direct)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text='📊 Statistiques avancées', command=self.sidebar_button_event)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        # Mode d’apparence
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Apparence :", anchor="w")
        self.appearance_mode_label.grid(row=4, column=0, padx=20, pady=(20, 0))

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionemenu.grid(row=5, column=0, padx=20, pady=(5, 20))

        # ======== Contenu principal ========
        self.entry = customtkinter.CTkEntry(self, placeholder_text="🔍 Rechercher un joueur")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        self.fullscreen_button = customtkinter.CTkButton(
            self, text="⛶ Plein écran", command=self.toggle_fullscreen, fg_color="transparent", border_width=2
        )
        self.fullscreen_button.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.is_fullscreen = True
        self.after(100, self.start_fullscreen)

    # ======== Fonctions ========
    def start_fullscreen(self):
        """Active le plein écran total au lancement."""
        self.overrideredirect(True)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.fullscreen_button.configure(text="🗗 Quitter le plein écran")

    def toggle_fullscreen(self):
        """Basculer entre plein écran total et fenêtre normale."""
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            # Supprime la bordure et la barre de titre
            self.overrideredirect(True)

            # Taille totale de l'écran
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            self.geometry(f"{screen_width}x{screen_height}+0+0")

            # Met à jour le texte du bouton
            self.fullscreen_button.configure(text="🗗 Quitter le plein écran")
        else:
            # Restaure la fenêtre normale
            self.overrideredirect(False)
            self.geometry("1100x580")

            # Met à jour le texte du bouton
            self.fullscreen_button.configure(text="⛶ Plein écran")


    '''def on_configure(self, event):
        """Détecte si l'utilisateur clique sur le bouton maximiser (haut à droite)."""
        try:
            # Vérifie si la fenêtre est maximisée par le système
            if self.state() == "zoomed" and not self.is_fullscreen:
                self.is_fullscreen = True
                self.overrideredirect(True)

                # Taille complète de l'écran
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                self.geometry(f"{screen_width}x{screen_height}+0+0")

            elif self.state() == "normal" and self.is_fullscreen:
                # Si on restaure depuis plein écran custom
                self.is_fullscreen = False
                self.overrideredirect(False)
                self.geometry("1100x580")
        except Exception:
            pass'''

    def choixvideo(self):
        """Sélectionner un fichier vidéo et lancer le traitement."""
        video_file = askopenfilename(
            title="Sélectionner une vidéo",
            filetypes=[("Fichiers vidéo", "*.mp4 *.avi *.mov *.mkv")]
        )
        if not video_file:
            messagebox.showwarning("Avertissement", "Aucune vidéo sélectionnée.")
            return

        try:
            main_instance = pcc.Main(video_file, 'video')
            main_instance.run()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lancer la vidéo.\n\n{e}")

    def direct(self):
        """Fenêtre de configuration du délai en mode direct."""
        fenetre = customtkinter.CTkToplevel(self)
        fenetre.title("Mode Direct")
        fenetre.geometry("300x220")
        fenetre.resizable(False, False)
        fenetre.grab_set()  # Fenêtre modale

        label_titre = customtkinter.CTkLabel(fenetre, text="⏱ Sélectionnez le délai de détection", font=customtkinter.CTkFont(size=14, weight="bold"))
        label_titre.pack(pady=15)

        valeurs = [str(i) for i in range(1, 101)]
        combobox = customtkinter.CTkComboBox(fenetre, values=valeurs, width=150)
        combobox.pack(pady=10)
        combobox.set("5")  # valeur par défaut

        label_resultat = customtkinter.CTkLabel(fenetre, text="")
        label_resultat.pack(pady=10)

        def valider():
            try:
                delay = int(combobox.get())
                label_resultat.configure(text=f"Délai sélectionné : {delay} s")
                pcc.main_delay(delay)
                fenetre.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'appliquer le délai.\n\n{e}")

        bouton_valider = customtkinter.CTkButton(fenetre, text="✅ Valider", command=valider)
        bouton_valider.pack(pady=10)

    def sidebar_button_event(self):
        """Ouvre la fenêtre de statistiques avancées."""
        try:
            pcc.debut(None, 0)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir les statistiques.\n\n{e}")

    def change_appearance_mode_event(self, new_mode: str):
        customtkinter.set_appearance_mode(new_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()
