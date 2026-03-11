import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.awt.event.*;
import java.util.Random;

/**
 * BMI-Rechner – Ein nerviger, hübscher BMI-Rechner mit vielen Pop-ups.
 * Kompilieren:  javac BMIRechner.java
 * Starten:      java BMIRechner
 */
public class BMIRechner extends JFrame {

    // ── Farben ──────────────────────────────────────────────────────────────
    private static final Color BG_DARK      = new Color(18,  18,  35);
    private static final Color BG_CARD      = new Color(30,  30,  55);
    private static final Color ACCENT       = new Color(99, 179, 237);
    private static final Color ACCENT2      = new Color(154, 117, 234);
    private static final Color TEXT_LIGHT   = new Color(237, 237, 255);
    private static final Color TEXT_MUTED   = new Color(140, 140, 180);
    private static final Color SUCCESS      = new Color( 72, 199, 142);
    private static final Color WARNING      = new Color(255, 183,  77);
    private static final Color DANGER       = new Color(240,  80,  80);

    // ── Felder ──────────────────────────────────────────────────────────────
    private JTextField nameField;
    private JTextField ageField;
    private JTextField weightField;
    private JTextField heightField;
    private JLabel     resultLabel;
    private JLabel     categoryLabel;
    private JProgressBar bmiBar;

    private final Random rng = new Random();

    // ════════════════════════════════════════════════════════════════════════
    public BMIRechner() {
        setTitle("🏋️ BMI-Rechner ULTRA™ 3000 🏋️");
        setDefaultCloseOperation(DO_NOTHING_ON_CLOSE);
        setSize(520, 680);
        setLocationRelativeTo(null);
        setResizable(false);

        // Fenster schließen → nervige Bestätigungs-Pop-ups
        addWindowListener(new WindowAdapter() {
            @Override public void windowClosing(WindowEvent e) {
                handleClose();
            }
        });

        buildUI();
        showWelcomePopups();
    }

    // ── UI aufbauen ──────────────────────────────────────────────────────────
    private void buildUI() {
        JPanel root = new JPanel(new BorderLayout());
        root.setBackground(BG_DARK);
        root.setBorder(new EmptyBorder(20, 20, 20, 20));

        root.add(buildHeader(),  BorderLayout.NORTH);
        root.add(buildForm(),    BorderLayout.CENTER);
        root.add(buildFooter(),  BorderLayout.SOUTH);

        setContentPane(root);
    }

    private JPanel buildHeader() {
        JPanel panel = new JPanel(new GridLayout(2, 1, 0, 4));
        panel.setBackground(BG_DARK);
        panel.setBorder(new EmptyBorder(0, 0, 16, 0));

        JLabel title = new JLabel("🏋️  BMI-Rechner ULTRA™", SwingConstants.CENTER);
        title.setFont(new Font("SansSerif", Font.BOLD, 26));
        title.setForeground(ACCENT);

        JLabel subtitle = new JLabel("Dein persönlicher Körper-Analyse-Assistent", SwingConstants.CENTER);
        subtitle.setFont(new Font("SansSerif", Font.ITALIC, 13));
        subtitle.setForeground(TEXT_MUTED);

        panel.add(title);
        panel.add(subtitle);
        return panel;
    }

    private JPanel buildForm() {
        JPanel card = new JPanel();
        card.setLayout(new BoxLayout(card, BoxLayout.Y_AXIS));
        card.setBackground(BG_CARD);
        card.setBorder(new CompoundBorder(
                new LineBorder(ACCENT2, 1, true),
                new EmptyBorder(24, 28, 24, 28)));

        nameField   = styledField("z. B.  Max Mustermann");
        ageField    = styledField("z. B.  25");
        weightField = styledField("in kg,  z. B.  75");
        heightField = styledField("in cm,  z. B.  178");

        card.add(fieldGroup("👤  Name:",          nameField));
        card.add(Box.createVerticalStrut(14));
        card.add(fieldGroup("🎂  Alter:",          ageField));
        card.add(Box.createVerticalStrut(14));
        card.add(fieldGroup("⚖️  Gewicht (kg):",  weightField));
        card.add(Box.createVerticalStrut(14));
        card.add(fieldGroup("📏  Größe (cm):",    heightField));
        card.add(Box.createVerticalStrut(24));

        // Berechnen-Button
        JButton calcBtn = new JButton("  🔬  BMI BERECHNEN  ");
        calcBtn.setFont(new Font("SansSerif", Font.BOLD, 15));
        calcBtn.setForeground(Color.WHITE);
        calcBtn.setBackground(ACCENT2);
        calcBtn.setFocusPainted(false);
        calcBtn.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        calcBtn.setBorder(new EmptyBorder(12, 20, 12, 20));
        calcBtn.setAlignmentX(Component.CENTER_ALIGNMENT);
        calcBtn.addMouseListener(new MouseAdapter() {
            @Override public void mouseEntered(MouseEvent e) { calcBtn.setBackground(ACCENT); }
            @Override public void mouseExited (MouseEvent e) { calcBtn.setBackground(ACCENT2); }
        });
        calcBtn.addActionListener(e -> startCalculation());

        card.add(calcBtn);
        card.add(Box.createVerticalStrut(24));

        // Ergebnis-Bereich
        resultLabel = new JLabel("??.?", SwingConstants.CENTER);
        resultLabel.setFont(new Font("SansSerif", Font.BOLD, 44));
        resultLabel.setForeground(ACCENT);
        resultLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        categoryLabel = new JLabel("Noch kein Ergebnis", SwingConstants.CENTER);
        categoryLabel.setFont(new Font("SansSerif", Font.BOLD, 16));
        categoryLabel.setForeground(TEXT_MUTED);
        categoryLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        bmiBar = new JProgressBar(0, 400);
        bmiBar.setValue(0);
        bmiBar.setStringPainted(false);
        bmiBar.setForeground(ACCENT2);
        bmiBar.setBackground(BG_DARK);
        bmiBar.setMaximumSize(new Dimension(Integer.MAX_VALUE, 10));
        bmiBar.setBorder(new EmptyBorder(0, 0, 0, 0));

        card.add(resultLabel);
        card.add(Box.createVerticalStrut(6));
        card.add(categoryLabel);
        card.add(Box.createVerticalStrut(12));
        card.add(bmiBar);

        return card;
    }

    private JPanel buildFooter() {
        JPanel panel = new JPanel(new FlowLayout(FlowLayout.CENTER));
        panel.setBackground(BG_DARK);
        panel.setBorder(new EmptyBorder(10, 0, 0, 0));

        JLabel hint = new JLabel("💡  BMI = Gewicht(kg) / Größe(m)²   |   v3.0  ©  BMI ULTRA™");
        hint.setFont(new Font("SansSerif", Font.PLAIN, 11));
        hint.setForeground(TEXT_MUTED);
        panel.add(hint);
        return panel;
    }

    // ── Hilfsmethoden für Felder ─────────────────────────────────────────────
    private JTextField styledField(String placeholder) {
        JTextField f = new JTextField(16);
        f.setFont(new Font("SansSerif", Font.PLAIN, 14));
        f.setForeground(TEXT_LIGHT);
        f.setBackground(BG_DARK);
        f.setCaretColor(ACCENT);
        f.setBorder(new CompoundBorder(
                new LineBorder(ACCENT2, 1, true),
                new EmptyBorder(8, 10, 8, 10)));
        // Placeholder-Simulation
        f.setText(placeholder);
        f.setForeground(TEXT_MUTED);
        f.addFocusListener(new FocusAdapter() {
            @Override public void focusGained(FocusEvent e) {
                if (f.getText().equals(placeholder)) {
                    f.setText("");
                    f.setForeground(TEXT_LIGHT);
                }
            }
            @Override public void focusLost(FocusEvent e) {
                if (f.getText().isBlank()) {
                    f.setText(placeholder);
                    f.setForeground(TEXT_MUTED);
                }
            }
        });
        return f;
    }

    private JPanel fieldGroup(String labelText, JTextField field) {
        JPanel p = new JPanel(new BorderLayout(0, 6));
        p.setBackground(BG_CARD);

        JLabel lbl = new JLabel(labelText);
        lbl.setFont(new Font("SansSerif", Font.BOLD, 13));
        lbl.setForeground(TEXT_LIGHT);

        p.add(lbl,   BorderLayout.NORTH);
        p.add(field, BorderLayout.CENTER);
        return p;
    }

    // ════════════════════════════════════════════════════════════════════════
    //   WILLKOMMENS-POP-UPS
    // ════════════════════════════════════════════════════════════════════════
    private void showWelcomePopups() {
        // Pop-up 1: Willkommen
        popup("🎉 Willkommen beim BMI-Rechner ULTRA™!",
              "Willkommen!\n\nDieses Programm wird deinen BMI berechnen.\n"
            + "Bitte sei auf viele hilfreiche Hinweise gefasst. 😊",
              JOptionPane.INFORMATION_MESSAGE);

        // Pop-up 2: Datenschutz
        popup("🔒 Datenschutzhinweis",
              "Deine Daten werden vertraulich behandelt.\n"
            + "(Nur du, dein Computer und das Universum sehen sie.)\n\n"
            + "Klicke OK um fortzufahren.",
              JOptionPane.WARNING_MESSAGE);

        // Pop-up 3: Haftungsausschluss
        popup("⚠️ Wichtiger Hinweis",
              "Der BMI ist nur ein grober Richtwert.\n"
            + "Er ersetzt keine ärztliche Beratung.\n\n"
            + "Bitte konsultiere einen Arzt, wenn du\n"
            + "medizinische Fragen hast.\n\n"
            + "Hast du das verstanden?",
              JOptionPane.WARNING_MESSAGE);

        // Captcha: Menschlichkeitsprüfung vor der Bestätigung
        if (!askMathCaptcha("die Nutzungsbedingungen zu bestätigen")) {
            showWelcomePopups(); // nochmal von vorne 😈
            return;
        }

        // Pop-up 4: Bestätigung des Hinweises
        int confirm = JOptionPane.showConfirmDialog(this,
              "Wirklich verstanden?\n\nHast du den Hinweis sorgfältig gelesen?",
              "✅ Bestätigung erforderlich",
              JOptionPane.YES_NO_OPTION,
              JOptionPane.QUESTION_MESSAGE);
        if (confirm != JOptionPane.YES_OPTION) {
            popup("😤 Bitte lesen!",
                  "Bitte lies den Hinweis noch einmal.\n\nDanke für deine Kooperation!",
                  JOptionPane.WARNING_MESSAGE);
            showWelcomePopups(); // nochmal von vorne 😈
        }

        // Pop-up 5: Bereit?
        popup("🚀 Los geht's!",
              "Super! Du kannst jetzt deine Daten eingeben.\n\n"
            + "Bitte gib alle Felder wahrheitsgemäß an.\n"
            + "Das Programm überprüft deine Eingaben! 🔍",
              JOptionPane.INFORMATION_MESSAGE);

        // Unnötiger Ladebalken: Systeminitialisierung
        showFakeLoader("⚙️ System wird initialisiert...", new String[]{
            "Verbinde mit BMI-Servern...",
            "Lade Körperdaten-Datenbank (247 MB)...",
            "Kalibriere digitale Gewichtssensoren...",
            "Initialisiere Quanten-BMI-Algorithmus...",
            "Überprüfe Systemintegrität...",
            "Installiere Updates (Schritt 1 von 1)...",
            "Starte neuronales Netz...",
            "System bereit! \u2705"
        });
    }

    // ════════════════════════════════════════════════════════════════════════
    //   BERECHNUNG MIT POP-UPS
    // ════════════════════════════════════════════════════════════════════════
    private void startCalculation() {
        // Pop-up: Wirklich berechnen?
        int sure = JOptionPane.showConfirmDialog(this,
              "Bist du sicher, dass du deinen BMI berechnen möchtest?\n\n"
            + "Das Ergebnis könnte überraschend sein! 😲",
              "🤔 Bist du sicher?",
              JOptionPane.YES_NO_OPTION,
              JOptionPane.QUESTION_MESSAGE);
        if (sure != JOptionPane.YES_OPTION) {
            popup("😅 OK!",
                  "Kein Problem! Nimm dir Zeit und komm zurück, wenn du bereit bist.",
                  JOptionPane.INFORMATION_MESSAGE);
            return;
        }

        // Unnötiger Ladebalken: Eingaben laden
        showFakeLoader("📥 Eingaben werden geladen...", new String[]{
            "Formular wird gelesen...",
            "Zeichen werden dekodiert...",
            "Tippfehler werden gesucht...",
            "Sonderzeichen werden escaped...",
            "Eingaben zwischengespeichert \u2705"
        });

        // Eingaben lesen
        String name   = getFieldText(nameField,   "z. B.  Max Mustermann");
        String ageStr = getFieldText(ageField,     "z. B.  25");
        String wtStr  = getFieldText(weightField,  "in kg,  z. B.  75");
        String htStr  = getFieldText(heightField,  "in cm,  z. B.  178");

        // ── Validierung ──────────────────────────────────────────────────────

        // Name
        if (name.isBlank()) {
            popup("❌ Fehlender Name",
                  "Bitte gib deinen Namen ein.\nAnonymität ist hier nicht erlaubt! 😤",
                  JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (name.length() < 2) {
            popup("❌ Name zu kurz",
                  "Ein Name mit weniger als 2 Zeichen? Das glaube ich nicht!\n"
                + "Bitte gib deinen echten Namen ein.",
                  JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (!name.matches("[a-zA-ZäöüÄÖÜß .\\-]+")) {
            popup("❌ Ungültiger Name",
                  "Ein Name darf nur Buchstaben, Leerzeichen und Bindestriche enthalten.\n"
                + "\"" + name + "\" sieht verdächtig aus! 🕵️",
                  JOptionPane.ERROR_MESSAGE);
            return;
        }

        // Alter
        int age;
        try {
            age = Integer.parseInt(ageStr.trim());
        } catch (NumberFormatException ex) {
            popup("❌ Ungültiges Alter",
                  "\"" + ageStr + "\" ist keine gültige Zahl.\nBitte gib dein Alter in Jahren ein.",
                  JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (age < 1) {
            popup("🍼 Zu jung!",
                  "Alter darf nicht kleiner als 1 sein.\n"
                + "Säuglinge brauchen keinen BMI-Rechner! 👶",
                  JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (age > 130) {
            popup("🧓 Realistisch bleiben!",
                  "Das älteste je verifizierte Alter ist 122 Jahre.\n"
                + "Bitte gib ein realistisches Alter ein.",
                  JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (age < 16) {
            popup("👦 Hinweis für Minderjährige",
                  "Der BMI-Rechner ist für Personen ab 16 Jahren gedacht.\n"
                + "Für Kinder und Jugendliche gelten andere Referenzwerte.\n\n"
                + "Bitte frage einen Arzt oder Elternteil.",
                  JOptionPane.WARNING_MESSAGE);
        }

        // Gewicht
        double weight;
        try {
            weight = Double.parseDouble(wtStr.trim().replace(",", "."));
        } catch (NumberFormatException ex) {
            popup("❌ Ungültiges Gewicht",
                  "\"" + wtStr + "\" ist keine gültige Zahl.\n"
                + "Beispiel: 75 oder 75.5",
                  JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (weight < 1) {
            popup("👻 Gewicht zu niedrig!",
                  "Ein Gewicht unter 1 kg? Das ist unmöglich.\nBitte gib dein echtes Gewicht ein.",
                  JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (weight > 700) {
            popup("🐋 Gewicht zu hoch!",
                  "Das schwerste je gemessene Gewicht bei einem Menschen\n"
                + "betrug ca. 635 kg.\n\nBitte gib ein realistisches Gewicht ein.",
                  JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (weight < 20) {
            int ok = JOptionPane.showConfirmDialog(this,
                    "Du hast " + weight + " kg eingegeben.\nIst das wirklich dein Gewicht?",
                    "⚠️ Sehr geringes Gewicht",
                    JOptionPane.YES_NO_OPTION,
                    JOptionPane.WARNING_MESSAGE);
            if (ok != JOptionPane.YES_OPTION) return;
        }

        // Größe
        double heightCm;
        try {
            heightCm = Double.parseDouble(htStr.trim().replace(",", "."));
        } catch (NumberFormatException ex) {
            popup("❌ Ungültige Größe",
                  "\"" + htStr + "\" ist keine gültige Zahl.\n"
                + "Beispiel: 178 oder 165.5",
                  JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (heightCm < 50) {
            popup("📐 Größe zu niedrig!",
                  "Eine Größe unter 50 cm? Das klingt nicht menschlich.\nBitte gib deine echte Größe ein.",
                  JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (heightCm > 280) {
            popup("🏀 Größe zu hoch!",
                  "Die größte je gemessene Person war 2,72 m groß.\n"
                + "Bitte gib eine realistische Größe ein.",
                  JOptionPane.ERROR_MESSAGE);
            return;
        }

        // Unnötiger Ladebalken: Daten überprüfen
        showFakeLoader("🔍 Daten werden überprüft...", new String[]{
            "Plausibilitätscheck läuft...",
            "Daten werden mit Weltgesundheitsorganisation abgeglichen...",
            "Anomalie-Detektor wird kalibriert...",
            "Körpermaße werden normiert...",
            "Anthropometrische Daten bestätigt \u2705"
        });

        // Pop-up: Eingaben bestätigen
        int confirmData = JOptionPane.showConfirmDialog(this,
              "Bitte bestätige deine Eingaben:\n\n"
            + "  👤  Name:      " + name     + "\n"
            + "  🎂  Alter:     " + age      + " Jahre\n"
            + "  ⚖️  Gewicht:   " + weight   + " kg\n"
            + "  📏  Größe:     " + heightCm + " cm\n\n"
            + "Sind diese Daten korrekt?",
              "📋 Eingaben bestätigen",
              JOptionPane.YES_NO_OPTION,
              JOptionPane.QUESTION_MESSAGE);
        if (confirmData != JOptionPane.YES_OPTION) {
            popup("✏️ Bitte korrigieren",
                  "Kein Problem! Passe deine Daten an und versuche es erneut.",
                  JOptionPane.INFORMATION_MESSAGE);
            return;
        }

        // Captcha: Menschlichkeitsprüfung vor der Berechnung
        if (!askMathCaptcha("die BMI-Berechnung zu starten")) {
            return;
        }

        // ── Berechnung ───────────────────────────────────────────────────────
        // Unnötiger Ladebalken: BMI berechnen
        showFakeLoader("🔬 BMI wird berechnet...", new String[]{
            "Schwerkraft wird gemessen...",
            "Körpermasse-Index-Formel wird geladen...",
            "Größe² wird berechnet (Schritt 1 von 1)...",
            "Quanten-Gewichts-Division läuft...",
            "Ergebnis wird auf 1 Dezimalstelle gerundet...",
            "Kategorie wird aus Datenbank abgerufen...",
            "Berechnung abgeschlossen \u2705"
        });

        double heightM = heightCm / 100.0;
        double bmi     = weight / (heightM * heightM);
        String category;
        Color  catColor;
        String emoji;
        String advice;

        if (bmi < 18.5) {
            category = "Untergewicht";
            catColor  = WARNING;
            emoji     = "🪶";
            advice    = "Du könntest etwas mehr essen. Ein Arzt kann dir dabei helfen!";
        } else if (bmi < 25.0) {
            category = "Normalgewicht";
            catColor  = SUCCESS;
            emoji     = "✅";
            advice    = "Perfekt! Bleib so und lebe gesund weiter!";
        } else if (bmi < 30.0) {
            category = "Übergewicht";
            catColor  = WARNING;
            emoji     = "🍔";
            advice    = "Etwas mehr Bewegung könnte nicht schaden. Du schaffst das!";
        } else if (bmi < 35.0) {
            category = "Adipositas Grad I";
            catColor  = DANGER;
            emoji     = "⚠️";
            advice    = "Bitte sprich mit einem Arzt über dein Gewicht.";
        } else if (bmi < 40.0) {
            category = "Adipositas Grad II";
            catColor  = DANGER;
            emoji     = "🚨";
            advice    = "Ein Arztbesuch ist dringend empfohlen!";
        } else {
            category = "Adipositas Grad III";
            catColor  = DANGER;
            emoji     = "🆘";
            advice    = "Bitte suche sofort ärztliche Hilfe!";
        }

        // UI aktualisieren
        resultLabel.setText(String.format("%.1f", bmi));
        resultLabel.setForeground(catColor);
        categoryLabel.setText(emoji + "  " + category);
        categoryLabel.setForeground(catColor);
        int barVal = (int) Math.min(bmi * 10, 400);
        bmiBar.setValue(barVal);
        bmiBar.setForeground(catColor);

        // Unnötiger Ladebalken: Ergebnis aufbereiten
        showFakeLoader("📊 Ergebnis wird aufbereitet...", new String[]{
            "BMI-Wert wird formatiert...",
            "Kategorie wird ermittelt...",
            "Persönliche Tipps werden generiert...",
            "Infografik wird erstellt...",
            "Ergebnis wird verschlüsselt...",
            "Ergebnis bereit \u2705"
        });

        // Pop-up: Ergebnis
        popup("🎯 Dein BMI-Ergebnis",
              "Hallo " + name + "! 👋\n\n"
            + "Dein BMI beträgt:   " + String.format("%.2f", bmi) + "\n"
            + "Kategorie:          " + emoji + " " + category + "\n\n"
            + advice,
              JOptionPane.INFORMATION_MESSAGE);

        // Extra-Pop-up: Gesundheitstipps
        showHealthTips(bmi, name);

        // Extra-Pop-up: Lustiger Kommentar
        showFunComment(bmi, name);

        // Extra-Pop-up: Nochmal berechnen?
        int again = JOptionPane.showConfirmDialog(this,
              "Möchtest du noch einmal berechnen?\n\n"
            + "(Vielleicht ist das Ergebnis beim nächsten Mal anders... 🤞)",
              "🔄 Nochmal?",
              JOptionPane.YES_NO_OPTION,
              JOptionPane.QUESTION_MESSAGE);
        if (again == JOptionPane.YES_OPTION) {
            popup("😄 Sehr gut!",
                  "Gib einfach neue Werte ein und klicke erneut auf\n"
                + "\"BMI BERECHNEN\".\n\nViel Erfolg! 🍀",
                  JOptionPane.INFORMATION_MESSAGE);
        } else {
            popup("👋 Auf Wiedersehen!",
                  "Danke, dass du den BMI-Rechner ULTRA™ verwendet hast!\n\n"
                + "Bleib gesund und munter! 💪",
                  JOptionPane.INFORMATION_MESSAGE);
        }
    }

    // ── Gesundheitstipps-Pop-up ───────────────────────────────────────────────
    private void showHealthTips(double bmi, String name) {
        String[] tips;
        if (bmi < 18.5) {
            tips = new String[]{
                "🥗 Iss kalorienreiche, nährstoffreiche Lebensmittel.",
                "🏃 Leichte Kraftübungen können helfen, Muskeln aufzubauen.",
                "💧 Trinke ausreichend Wasser (mindestens 2 Liter pro Tag).",
                "😴 Achte auf ausreichend Schlaf (7–9 Stunden).",
                "👨‍⚕️ Bitte konsultiere einen Arzt oder Ernährungsberater."
            };
        } else if (bmi < 25.0) {
            tips = new String[]{
                "✅ Du bist im gesunden Bereich – weiter so!",
                "🏃 30 Minuten Bewegung täglich halten dich fit.",
                "🥦 Achte auf eine ausgewogene Ernährung.",
                "💧 2–3 Liter Wasser täglich sind ideal.",
                "😴 7–9 Stunden Schlaf pro Nacht sind empfohlen."
            };
        } else {
            tips = new String[]{
                "🚶 Fange mit täglichen Spaziergängen an.",
                "🥗 Reduziere zuckerhaltige Lebensmittel und Getränke.",
                "💧 Trinke mehr Wasser statt Softdrinks.",
                "📱 Apps wie MyFitnessPal können beim Abnehmen helfen.",
                "👨‍⚕️ Ein Arzt oder Ernährungsberater kann helfen."
            };
        }

        StringBuilder msg = new StringBuilder();
        msg.append("Hier sind einige Tipps speziell für dich, ").append(name).append(":\n\n");
        for (String tip : tips) {
            msg.append(tip).append("\n");
        }

        popup("💡 Gesundheitstipps für dich", msg.toString(), JOptionPane.INFORMATION_MESSAGE);
    }

    // ── Lustiger Kommentar ────────────────────────────────────────────────────
    private void showFunComment(double bmi, String name) {
        String[] comments;
        if (bmi < 18.5) {
            comments = new String[]{
                "Du bist so leicht, der Wind könnte dich wegpusten! 🌬️",
                "Hast du heute schon gegessen? 🍕",
                "Selbst eine Feder wiegt mehr als du... fast. 🪶",
                "Bitte iss noch einen Burger. Nur einen. 🍔"
            };
        } else if (bmi < 25.0) {
            comments = new String[]{
                "Du bist perfekt! Gratuliere, du hast das Leben gemeistert. 🏆",
                "Leonardo da Vinci hätte dich als Modell gezeichnet. 🎨",
                "Der Goldene Schnitt ist nichts gegen dein Gewicht! ✨",
                "Sportstars beneiden dich. Wahrscheinlich. 🥇"
            };
        } else if (bmi < 30.0) {
            comments = new String[]{
                "Ein bisschen Polsterung ist doch gemütlich, oder? 🛋️",
                "Du bist gut gepolstert für den Winter! ❄️",
                "Steh mal auf – das zählt schon als Sport. 🧘",
                "Dein Sofa vermisst dich bestimmt. 📺"
            };
        } else {
            comments = new String[]{
                "Du bist dein eigenes Schwergewicht-Boxteam! 🥊",
                "Schwerkraft? Nie gehört. Du hast deine eigene. 🌍",
                "Du bist so schwer, Satelliten umkreisen dich. 🛰️",
                "Wenn du springst, erzittert die Erde. Buchstäblich. 🌋"
            };
        }

        String comment = comments[rng.nextInt(comments.length)];
        popup("😄 Spaß-Kommentar des Tages",
              name + ", heute wird dir gesagt:\n\n\"" + comment + "\"\n\n"
            + "(Nicht zu ernst nehmen – alles mit Humor! 😉)",
              JOptionPane.INFORMATION_MESSAGE);
    }

    // ════════════════════════════════════════════════════════════════════════
    //   FAKE LADEBALKEN
    // ════════════════════════════════════════════════════════════════════════
    /**
     * Zeigt einen modalen Dialog mit einem animierten (aber völlig unnötigen)
     * Fortschrittsbalken, der die übergebenen Schritt-Texte nacheinander anzeigt.
     * Der Dialog schließt sich nach Ablauf automatisch.
     */
    private void showFakeLoader(String title, String[] steps) {
        JDialog dlg = new JDialog(this, title, true);
        dlg.setDefaultCloseOperation(JDialog.DO_NOTHING_ON_CLOSE);
        dlg.setSize(440, 175);
        dlg.setLocationRelativeTo(this);
        dlg.setResizable(false);

        JPanel panel = new JPanel(new BorderLayout(0, 14));
        panel.setBackground(BG_CARD);
        panel.setBorder(new CompoundBorder(
                new LineBorder(ACCENT2, 1),
                new EmptyBorder(22, 26, 22, 26)));

        JLabel statusLbl = new JLabel("\u2699\uFE0F  " + steps[0], SwingConstants.LEFT);
        statusLbl.setFont(new Font("SansSerif", Font.PLAIN, 13));
        statusLbl.setForeground(TEXT_LIGHT);

        JProgressBar bar = new JProgressBar(0, 100);
        bar.setValue(0);
        bar.setStringPainted(true);
        bar.setFont(new Font("SansSerif", Font.BOLD, 11));
        bar.setForeground(ACCENT2);
        bar.setBackground(BG_DARK);
        bar.setPreferredSize(new Dimension(0, 22));

        panel.add(statusLbl, BorderLayout.CENTER);
        panel.add(bar,       BorderLayout.SOUTH);
        dlg.setContentPane(panel);

        // Each step takes ~ticksPerStep x 40 ms = 720 ms
        int ticksPerStep = 18;
        int[] tick = {0};
        int totalTicks = steps.length * ticksPerStep;

        // javax.swing.Timer fires on the EDT; the modal dialog runs its own
        // nested event loop, so Timer events are still dispatched correctly.
        Timer timer = new Timer(40, null);
        timer.addActionListener(e -> {
            tick[0]++;
            int stepIdx = Math.min(tick[0] / ticksPerStep, steps.length - 1);
            statusLbl.setText("\u2699\uFE0F  " + steps[stepIdx]);
            int pct = Math.min(tick[0] * 100 / totalTicks, 100);
            bar.setValue(pct);
            bar.setString(pct + "%");
            if (tick[0] >= totalTicks) {
                timer.stop();
                dlg.dispose();
            }
        });

        timer.start();
        dlg.setVisible(true); // blocks in the modal event loop; timer still fires
    }

    // ════════════════════════════════════════════════════════════════════════
    //   RECHENAUFGABE (CAPTCHA)
    // ════════════════════════════════════════════════════════════════════════
    /**
     * Legt dem Nutzer eine zufällige Rechenaufgabe vor.
     * Gibt {@code true} zurück, wenn die Aufgabe korrekt gelöst wurde,
     * {@code false} wenn alle Versuche aufgebraucht sind oder der Dialog
     * abgebrochen wurde.
     *
     * @param purpose wird im Text angezeigt, z. B. "die Berechnung zu starten"
     */
    private boolean askMathCaptcha(String purpose) {
        final int MAX = 3;
        int remaining = MAX;

        while (remaining > 0) {
            // Neue Aufgabe für jeden Versuch generieren
            int a = rng.nextInt(12) + 2;
            int b = rng.nextInt(12) + 2;
            int opIdx = rng.nextInt(3);
            String op;
            int correct;

            if (opIdx == 0) {
                op = "+";  correct = a + b;
            } else if (opIdx == 1) {
                if (a < b) { int t = a; a = b; b = t; }
                op = "-";  correct = a - b;
            } else {
                a = rng.nextInt(9) + 2;
                b = rng.nextInt(9) + 2;
                op = "\u00d7";  correct = a * b;
            }

            int attemptNum = MAX - remaining + 1;
            String input = JOptionPane.showInputDialog(this,
                  "\uD83D\uDD10  Anti-Roboter-Verifikation  (" + attemptNum + " / " + MAX + ")\n\n"
                + "Um " + purpose + ", löse bitte diese Aufgabe:\n\n"
                + "          " + a + "  " + op + "  " + b + "  =  ?\n\n"
                + "Gib deine Antwort als ganze Zahl ein:",
                  "\uD83E\uDDEE Rechenaufgabe – Menschlichkeitsprüfung",
                  JOptionPane.QUESTION_MESSAGE);

            if (input == null) {
                popup("\uD83D\uDEAB Aufgabe abgebrochen",
                      "Du hast die Rechenaufgabe nicht gelöst.\nVorgang wird abgebrochen.",
                      JOptionPane.WARNING_MESSAGE);
                return false;
            }

            int ans;
            try {
                ans = Integer.parseInt(input.trim());
            } catch (NumberFormatException ex) {
                remaining--;
                popup("\u274C Keine ganze Zahl!",
                      "\"" + input + "\" ist keine ganze Zahl!\n"
                    + "Noch " + remaining + " Versuch(e) übrig.",
                      JOptionPane.ERROR_MESSAGE);
                continue;
            }

            if (ans == correct) {
                popup("\u2705 Richtig!",
                      "Korrekte Antwort! Du bist (höchstwahrscheinlich) kein Roboter. \uD83C\uDF89",
                      JOptionPane.INFORMATION_MESSAGE);
                return true;
            }

            remaining--;
            if (remaining > 0) {
                popup("\u274C Falsch!",
                      "Leider falsch. Richtige Antwort war:  " + correct + "\n\n"
                    + "Noch " + remaining + " Versuch(e) übrig.\n"
                    + "Tipp: Mit Finger zählen geht's leichter! \uD83D\uDC4B",
                      JOptionPane.ERROR_MESSAGE);
            } else {
                popup("\uD83E\uDD16 Roboter erkannt!",
                      "Alle " + MAX + " Versuche aufgebraucht!\nRichtige Antwort: " + correct + "\n\n"
                    + "Das Programm geht davon aus, dass du ein Roboter bist.\n"
                    + "Vorgang wird abgebrochen! \uD83D\uDE08",
                      JOptionPane.ERROR_MESSAGE);
            }
        }
        return false;
    }

    // ── Fenster schließen ─────────────────────────────────────────────────────
    private void handleClose() {
        int step1 = JOptionPane.showConfirmDialog(this,
              "Möchtest du das Programm wirklich beenden?",
              "❓ Beenden?",
              JOptionPane.YES_NO_OPTION,
              JOptionPane.QUESTION_MESSAGE);
        if (step1 != JOptionPane.YES_OPTION) return;

        int step2 = JOptionPane.showConfirmDialog(this,
              "Bist du WIRKLICH sicher?\n\nDas Programm wird geschlossen und dein Ergebnis verschwindet!",
              "⚠️ Wirklich beenden?",
              JOptionPane.YES_NO_OPTION,
              JOptionPane.WARNING_MESSAGE);
        if (step2 != JOptionPane.YES_OPTION) return;

        // Captcha: Menschlichkeitsprüfung vor dem Schließen
        if (!askMathCaptcha("das Programm zu beenden")) {
            popup("😄 Gut so!",
                  "Du hast die Aufgabe nicht gelöst.\nDas Programm bleibt geöffnet. 🎉",
                  JOptionPane.INFORMATION_MESSAGE);
            return;
        }

        // Unnötiger Ladebalken: Programm beenden
        showFakeLoader("👋 Programm wird beendet...", new String[]{
            "Sitzungsdaten werden gelöscht...",
            "Verbindung zu BMI-Servern wird getrennt...",
            "Temporäre Dateien werden entfernt...",
            "Abschlussbericht wird erstellt...",
            "Auf Wiedersehen \uD83D\uDC4B"
        });

        popup("😢 Auf Wiedersehen!",
              "Schade, dass du gehst.\n\nKomm bald wieder! 👋\n\n"
            + "(Der BMI-Rechner ULTRA™ wird dich vermissen.)",
              JOptionPane.INFORMATION_MESSAGE);

        dispose();
        System.exit(0);
    }

    // ── Hilfsmethoden ─────────────────────────────────────────────────────────
    private void popup(String title, String message, int type) {
        JOptionPane.showMessageDialog(this, message, title, type);
    }

    private String getFieldText(JTextField field, String placeholder) {
        String text = field.getText().trim();
        return text.equals(placeholder) ? "" : text;
    }

    // ════════════════════════════════════════════════════════════════════════
    public static void main(String[] args) {
        // System Look & Feel versuchen, dann Nimbus, dann Standard
        try {
            for (UIManager.LookAndFeelInfo info : UIManager.getInstalledLookAndFeels()) {
                if ("Nimbus".equals(info.getName())) {
                    UIManager.setLookAndFeel(info.getClassName());
                    break;
                }
            }
        } catch (Exception ignored) { }

        SwingUtilities.invokeLater(() -> {
            BMIRechner app = new BMIRechner();
            app.setVisible(true);
        });
    }
}
