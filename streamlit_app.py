import streamlit as st
import pandas as pd
import requests
import io

# ========================
# Configuration de la page
# ========================
st.set_page_config(page_title="Détection de faux billets", layout="centered")

st.title("💶 Détection automatique de faux billets")
st.write("Uploader un fichier CSV contenant **les 6 caractéristiques géométriques** des billets. Le fichier **ne doit pas contenir** la colonne `is_genuine`.")

# ========================
# Upload de fichier
# ========================
uploaded_file = st.file_uploader("📤 Choisir un fichier CSV", type=["csv"])

if uploaded_file:
    try:
        # Lire et afficher un aperçu du fichier
        df = pd.read_csv(uploaded_file, sep=";")
        st.subheader("📄 Aperçu du fichier importé")
        st.dataframe(df.head())

        # Vérification des colonnes attendues
        expected_cols = ['length', 'height_left', 'height_right', 'margin_up', 'margin_low', 'diagonal']
        if not set(expected_cols).issubset(df.columns):
            st.error(f"❌ Le fichier doit contenir exactement ces colonnes : {expected_cols}")
        else:
            # Bouton pour lancer la prédiction
            if st.button("🔍 Lancer la prédiction"):
                with st.spinner("Envoi du fichier à l'API..."):
                    api_url = "http://127.0.0.1:8000/predict/"  # Modifier si l’API est en ligne

                    # Réinitialiser le curseur du fichier (important)
                    uploaded_file.seek(0)

                    # Envoyer le fichier à l'API
                    files = {
                        "file": ("billets_production.csv", uploaded_file, "text/csv")
                    }
                    response = requests.post(api_url, files=files)

                    if response.status_code == 200:
                        result = response.json()
                        predictions = pd.DataFrame(result['predictions'])

                        # 🔧 Convertir en entier (sinon map échoue)
                        predictions['prediction'] = predictions['prediction'].astype(int)

                        # Ajouter une colonne étiquette lisible
                        predictions['prediction_label'] = predictions['prediction'].map({
                            0: "❌ Faux billet",
                            1: "✅ Vrai billet"
                        })


                        st.success("✅ Prédictions reçues avec succès !")
                        st.subheader("📋 Résultat des prédictions")
                        st.dataframe(predictions[['length', 'height_left', 'height_right',
                                                  'margin_up', 'margin_low', 'diagonal',
                                                  'prediction_label']])

                        # Statistiques
                        st.subheader("📊 Statistiques des prédictions")
                        counts = predictions["prediction_label"].value_counts()
                        st.write(counts)

                        # Graphique
                        st.bar_chart(counts)

                    else:
                        st.error(f"Erreur de l'API : {response.json().get('error', 'Erreur inconnue')}")
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement du fichier : {e}")
