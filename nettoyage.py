import pandas as pd

# ===== 1. LIRE =====
dem = pd.read_excel("data/raw/demographie_professionnels_sante.xlsx")

# ===== 2. CORRIGER =====

# Problème 1 : la faute de frappe
dem["specialites"] = dem["specialites"].replace("18-Othoponistes", "18-Orthophonistes")

# Problème 2 : les "ND" dans la colonne 2025
print("Avant :", dem["effectif_2025"].dtype)
dem["effectif_2025"] = pd.to_numeric(dem["effectif_2025"], errors="coerce")
print("Après :", dem["effectif_2025"].dtype)

# ===== 3. VÉRIFIER =====
print(dem["specialites"].unique())


# Problème 3 : passer du format large au format long
colonnes_annees = [c for c in dem.columns if c.startswith("effectif_")]

dem = dem.melt(
    id_vars=["departement", "specialites", "tranche_age"],  # colonnes qu'on garde telles quelles
    value_vars=colonnes_annees,                             # colonnes à "faire fondre" en lignes
    var_name="annee",                                       # nom de la nouvelle colonne des années
    value_name="effectif"                                   # nom de la nouvelle colonne des valeurs
)

# "effectif_2012" -> 2012 (on enlève le texte et on garde le nombre)
dem["annee"] = dem["annee"].str.replace("effectif_", "").astype(int)

# Comme 2025 fait maintenant partie de la colonne "effectif", on la convertit en nombres
dem["effectif"] = pd.to_numeric(dem["effectif"], errors="coerce")

print(dem.head(15))
print("Nombre de lignes :", len(dem))

# Problème 4 : les espaces en trop dans les tranches d'âge
# "11- 75 ans et plus"  ->  "11-75 ans et plus"
dem["tranche_age"] = dem["tranche_age"].str.replace("- ", "-")

# Problème 5 : repérer la ligne "Ensemble" (le total)
# La ligne "00-Ensemble" est déjà la somme de toutes les tranches d'âge.
# Si on l'additionne avec les autres, on compte tout en double.
dem["est_total"] = dem["tranche_age"] == "00-Ensemble"

# Problème 6 : un code département simple
# "02A -Corse-du-Sud"  ->  "2A"   (comme dans les autres fichiers)
dem["dep_code"] = dem["departement"].str[1:3]

print(dem["tranche_age"].unique())
print(dem["dep_code"].unique())

# ===== 4. ENREGISTRER =====
dem.to_csv("data/clean/demographie.csv", index=False)
print("Fichier propre enregistré !")















# ==========================================================
# FICHIER 2 : POPULATION
# ==========================================================

# 1. LIRE (en précisant que les codes sont du texte)
pop = pd.read_excel("data/raw/population_corse.xlsx",dtype={"code_commune": str, "epci_code": str})

# 2. CORRIGER : séparer "42.09, 8.80" en deux colonnes
coords = pop["centroid_com"].str.split(",", expand=True)
pop["latitude"] = pd.to_numeric(coords[0])
pop["longitude"] = pd.to_numeric(coords[1])

# On garde seulement les colonnes utiles
pop = pop[["code_commune", "commune", "population", "dep_code",
           "epci_code", "epci_name", "latitude", "longitude"]]

# 3. VÉRIFIER
print(pop.head())
print("Nombre de communes :", len(pop))
print("Population totale :", pop["population"].sum())

# 4. ENREGISTRER
pop.to_csv("data/clean/communes.csv", index=False)
print("Fichier communes enregistré !")













# ==========================================================
# FICHIER 3 : CARREAUX
# ==========================================================

# ----- 1. LIRE -----
car = pd.read_csv(
    "data/raw/carreaux_1km_corse.csv",
    sep=";",
    dtype={"code_commune": str}
)
print("Avant :", len(car), "carrés,", car["code_commune"].nunique(), "codes différents")

# ----- 2. CORRIGER -----

# Problème 1 : les codes collés -> on garde le premier
car["code_commune"] = car["code_commune"].str.split(",").str[0]

# Problème 2 : on garde seulement les colonnes utiles
car = car[["code_commune", "pop", "pop65p"]]

# Problème 4 : on additionne les carrés de chaque commune
age = car.groupby("code_commune").sum().reset_index()

# Problème 3 : on arrondit (pas de "49,37 habitants")
age = age.round()

# ----- 3. VÉRIFIER -----
print("Après :", len(age), "communes")
print(age.head())

# ----- 4. ENREGISTRER -----
age.to_csv("data/clean/age_par_commune.csv", index=False)
print("Fichier age_par_commune enregistré !")












# ==========================================================
# FICHIER 4 : PROFESSIONNELS DE SANTÉ
# ==========================================================

# ----- 1. LIRE -----
pro = pd.read_excel(
    "data/raw/professionnels_sante.xlsx",
    dtype={"code_commune": str}
)
print("Avant :", pro.shape)   # (nombre de lignes, nombre de colonnes)

# ----- 2. CORRIGER -----

# Problème 2 : séparer les coordonnées en latitude / longitude
coords = pro["Coordonnées"].str.split(",", expand=True)
pro["latitude"] = pd.to_numeric(coords[0])
pro["longitude"] = pd.to_numeric(coords[1])

# Problème 4 : des noms de colonnes simples
pro = pro.rename(columns={
    "Nom du professionnel": "nom",
    "Civilité": "civilite",
    "Profession": "profession",
    "Nature d'exercice": "nature_exercice",
})

# Problème 1 : on garde seulement les colonnes utiles
pro = pro[["nom", "civilite", "profession", "nature_exercice",
           "code_commune", "latitude", "longitude"]]

# Problème 3 : un numéro unique pour chaque ligne (1, 2, 3, ...)
pro.insert(0, "id_professionnel", range(1, len(pro) + 1))

# ----- 3. VÉRIFIER -----
print("Après :", pro.shape)
print(pro.head())
print(pro["profession"].value_counts().head(5))

# ----- 4. ENREGISTRER -----
pro.to_csv("data/clean/professionnels.csv", index=False)
print("Fichier professionnels enregistré !")








# ==========================================================
# FICHIER 5 : ÉTABLISSEMENTS DE SANTÉ
# ==========================================================

# ----- 1. LIRE -----
# Problème 1 : on lit seulement l'onglet "Feuil1"
etab = pd.read_excel(
    "data/raw/etablissements_sanitaire.xlsx",
    sheet_name="Feuil1",
    dtype={"code_commune": str, "Numéro FINESS ET": str}
)
print("Types différents avant :", etab["libelle_categorie_etablissement"].nunique())

# ----- 2. CORRIGER -----

# Problème 2 : séparer les coordonnées
coords = etab["coord"].str.split(",", expand=True)
etab["latitude"] = pd.to_numeric(coords[0])
etab["longitude"] = pd.to_numeric(coords[1])

# Problème 3 : regrouper les ~80 types en 6 familles
def famille(categorie):
    c = categorie.lower()                      # tout en minuscules
    if "pharmacie" in c:
        return "Pharmacie"
    if "hospitalier" in c:
        return "Hôpital"
    if c in ("maison de santé (l.6223-3)", "centre de santé"):
        return "Maison / centre de santé"
    if "personnes âgées" in c:
        return "EHPAD"
    if "laboratoire" in c:
        return "Laboratoire"
    return "Autre"

etab["famille"] = etab["libelle_categorie_etablissement"].map(famille)

# Problème 4 : des noms de colonnes simples
etab = etab.rename(columns={
    "Numéro FINESS ET": "finess",
    "libelle_categorie_etablissement": "categorie",
})

# On garde les colonnes utiles
etab = etab[["finess", "nom_etablissement", "categorie", "famille",
             "code_commune", "latitude", "longitude"]]

# ----- 3. VÉRIFIER -----
print(etab["famille"].value_counts())

# ----- 4. ENREGISTRER -----
etab.to_csv("data/clean/etablissements.csv", index=False)
print("Fichier etablissements enregistré !")