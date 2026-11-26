"""B4 : errata R3 des pièces 38, 85, 86, 87, 88. Copie de la pièce d'origine, ajout d'un onglet « Erratum R2 » en tête par UNO
(LibreOffice), recalcul, enregistrement xlsx. Le contrôle des onglets d'origine est fait par b4_errata_check.py.

Exécution : ce module s'exécute dans l'interpréteur Python intégré à LibreOffice, comme macro (fonction errata), par
  soffice --headless -env:UserInstallation=file://<profil> "vnd.sun.star.script:b4_errata.py$errata?language=Python&location=user"
après copie du fichier dans <profil>/user/Scripts/python/ (voir executer.sh). La variable d'environnement LOT5_ICI donne le
dossier scripts/lot5-tva ; les chemins des pièces d'origine sont lus dans cache/entrees.json (écrit par s00_charger.py).
Il peut aussi être lancé par un interpréteur disposant du module uno, LibreOffice étant alors démarré en écoute (b4_recalc.connect)."""
import sys, os, shutil, json
import uno
from com.sun.star.beans import PropertyValue
def pv(n,v): p=PropertyValue(); p.Name=n; p.Value=v; return p
ICI=os.environ.get('LOT5_ICI') or os.path.dirname(os.path.abspath(__file__))
DST=os.path.join(ICI,'cache','pieces')+os.sep
H=['Onglet de la pièce','Cellule(s)','Texte ou valeur de la pièce','Correction','Renvoi']
INTRO='Onglet ajouté le 25/11/2026. Le contenu des autres onglets est inchangé, valeurs et formules comprises. Les corrections ci-dessous se lisent avec la section 2.5 de la réponse et les annexes 161 à 164.'
E={}
E['38']=('38-rf-anomalies-tva.xlsx','38-R3-rf-anomalies-tva-erratum.xlsx',[
 ('1. Extrait du fichier caisse','D1, E1','Base HT du fichier (BUGGEE) ; TVA encaissee (CORRECTE)','VAT_base (base HT d\'affichage, égale au palier TTC moins le taux lu en euros) ; tax_amount (TVA liquidée par la caisse)','161, onglet « Paliers lignes G »'),
 ('2. Exemple ticket n2','B1, C1, D1','Base HT (BUGGEE) ; TVA encaissee (CORRECTE) ; Base correcte = TVA / taux','VAT_base ; tax_amount (TVA liquidée) ; base HT = palier TTC − tax_amount','163, onglet « Errata CSV »'),
 ('2. Exemple ticket n2','D2','14,30','14,27 (palier 10 % de 15,70 € − taxe 1,43 €)','163, onglet « Errata CSV »'),
 ('2. Exemple ticket n2','D3','4,35','4,33 (palier 20 % de 5,20 € − taxe 0,87 €)','idem'),
 ('2. Exemple ticket n2','D4','18,65','18,60 (= 14,27 + 4,33 = 20,90 − 2,30)','idem'),
 ('3. Totaux mauvaise colonne','G1','CA TTC encaisse','Σ TTC des tickets du journal de TVA (tot_ttc)','tableau 53'),
 ('3. Totaux mauvaise colonne et 4. Totaux bonne colonne','F1','= Total reconstitue (en-tête saisi comme une formule, sans valeur en cache ; évalué, il donne une erreur)','cellule convertie en texte « = Total reconstitue », seule modification apportée aux onglets d\'origine (aucune valeur d\'origine n\'existait)','défaut de saisie de la pièce d\'origine'),
 ('4. Totaux bonne colonne','B1, C1, E1','Base HT 10 % (=TVA/taux) ; Base HT 20 % (=TVA/taux) ; + TVA encaissee','base déduite de tax_amount (tax_amount / taux) ; + Σ tax_amount (TVA liquidée). La base HT de la caisse est palier − tax_amount : 296 104,33 / 64 713,33 € en 2022-2023','tableau 47 ; 163, onglet « Bases »'),
 ('5. Comparaison et comptabilite','F1, I1, I2:I5, K2:K5','TVA nous ; Base HT nous (360 819,30 / 391 587,60 / 388 894,15 ; total 1 141 301,05) ; écart de base 0,92 / −8,26 / 31,25 ; total 23,91','TVA liquidée ; base HT de la caisse (palier − taxe) 360 817,66 / 391 592,84 / 388 901,23 ; total 1 141 311,73 ; écart caisse − comptabilité −0,72 / −3,02 / +38,33 ; total +34,59','tableau 47 ; 163, onglets « Bases » et « Errata CSV »')])
E['85']=('85-R2-tva-bouclage.xlsx','85-R3-tva-bouclage-journaux-G-29588-lignes-identite-VAT-base-erratum.xlsx',[
 ('Méthode','A29','« (VAT_base est arrondie au 5 centimes) »','VAT_base vaut exactement palier TTC − taux (29 588 lignes sur 29 588) ; l\'écart de 0,05 € au plus de la colonne I vient de l\'arrondi de la taxe. Les formules restent justes.','tableau 50, dernière ligne ; 161, onglet « Paliers lignes G »'),
 ('Calcul-G1, Calcul-G2, Calcul-G3','A18','« (arrondi au 5 centimes) »','même correction que Méthode, A29','idem'),
 ('Méthode','A6','« TVA de la ligne figée à l\'encaissement »','TVA de la ligne liquidée par la caisse','section 2.5 (vocabulaire)'),
 ('Méthode','A10, A15, A17 ; Calcul-G1 à G3, A4 et A6 ; Bouclage-3ex, A1, A8 à A10, A16, A23','« TVA encaissée »','TVA liquidée (Σ tax_amount)','idem'),
 ('Méthode','A10 ; Calcul-G1 à G3, A6','« Base déduite = TVA encaissée / taux légal »','grandeur conservée comme lecture ; la base HT de la caisse est palier TTC − tax_amount','tableau 47'),
 ('Méthode','A23','« la base déduite de cette taxe rejoint les bases comptabilisées à 23,91 € près sur trois ans »','la base HT de la caisse (palier − taxe) rejoint les bases comptabilisées à 34,59 € près sur trois ans (0,003 %)','tableau 47 ; 163, onglet « Bases »'),
 ('Méthode','A31 ; Calcul-G1 à G3, A21','« moins de 20 € de boissons alcoolisées sur le ticket » ; « (boissons alcoolisées du ticket) »','part TTC des articles paramétrés à 20 % (entre 0 et 20 €) ; les articles paramétrés à 20 % ne sont pas tous des boissons alcoolisées et inversement (162)','tableau 51'),
 ('Méthode','A25','attribution de l\'excédent de 192,33 € à la TVA sur pourboire (185,24 €)','compatible avec une TVA à 10 % sur le compte 706800, sans être établie ; la TVA légalement due excède le 445710 de 444,41 €','tableau 46 ; 163, onglet « Étalons »'),
 ('Bouclage-3ex','ensemble','source des tableaux 48 et 53 de la réponse R1','les tableaux 48 et 53 ne sont pas tirés de « Bouclage-3ex » : tableau 48 = 163, onglet « Étalons » ; tableau 53 = pièces 38 à 40','tableaux 48 et 53')])
E['86']=('86-R1-tva-rapprochement.xlsx','86-R3-tva-rapprochement-caisse-tickets-comptabilite-erratum.xlsx',[
 ('1. Rapprochement TVA','D1, D2:D11','« TVA recalculee depuis le detail des tickets (annexe C) » : 42 422,26 / 46 416,20 / 46 227,47 ; total 135 065,93','TVA calculée aux taux retenus par le service (colonne E). Ce n\'est pas la TVA due : la TVA légalement due est 42 770,29 / 46 606,01 / 46 152,80 ; total 135 529,10','162, onglet « Synthèse »'),
 ('1. Rapprochement TVA','E1','« TVA collectee comptabilisee et reversee (445710 / 706300 / 706000) »','TVA collectée comptabilisée (445710) sur les lignes TOTAL ; TVA théorique (706300 × 10 %, 706000 × 20 %) sur les lignes par taux','tableau 46'),
 ('2. Bases par taux','D1, D2:D8, G2:G8','base déduite de la TVA encaissée (tax_amount / taux) ; écart 23,91 €','base HT de la caisse = palier − tax_amount : écart caisse − comptabilité −1,54 / +0,82 / −3,75 / +0,73 / +177,68 / −139,35 ; total +34,59','tableau 47 ; 163, onglet « Bases »'),
 ('3. Controle par ticket','B5, F5','16 624 tickets ; écart −96,64 €','périmètre des annexes C et H, seconde série comprise (16 624 notes) ; à distinguer de l\'écart de 205,22 € mesuré sur les 16 605 tickets du journal de TVA G','tableau 46 ; point 2.2.4 e'),
 ('4. Les six colonnes p47','B2:B7','« colonne native de l\'export » ; « recopie ... (calcul du service) » pour les quatre dernières','les quatre dernières colonnes sont la recopie exacte de VAT_base et de tax_amount selon le taux ; le service indique que les deux dernières proviennent de son calcul (p. 47)','tableau 55'),
 ('5. Erreurs de taux annexe C','C2:C4','10 414 / 10 891 / 10 630 lignes signalées','ces nombres excluent les lignes à TTC nul ; lignes signalées : 10 464 / 10 935 / 10 648 (32 047)','164'),
 ('5. Erreurs de taux annexe C','E1','« TVA au taux legal (col. F appliquee) »','TVA aux taux retenus par le service (colonne E) ; sur les lignes de nature déterminée, le taux du service diffère du taux légal sur 2 223 lignes (909 signalées, 1 314 non signalées)','164, onglet « Synthèse »'),
 ('6. Methode','B4, B5','« TVA figee par la caisse a chaque paiement » ; « affecte de son taux legal, en appliquant la correction de taux portee par le service »','TVA liquidée par la caisse ; taux retenu par le service (colonne E), distinct du taux légal','162 ; 164')])
E['87']=('87-R1-tva-colonnes-ef.xlsx','87-R3-tva-colonnes-E-et-F-annexes-C-corrections-de-taux-erratum.xlsx',[
 ('3 Incidence reelle','G14, A16','B − C = −18,76 € ; « tombe a 18,76 EUR de la TVA effectivement reversee » ; « Leur incidence sur la TVA due est nulle »','l\'écart de −18,76 € est une coïncidence par compensation, et non une concordance : la colonne B mêle 30 364 artefacts corrigés, 822 lignes justes rendues fausses, 87 lignes redressées vers le mauvais taux, et laisse 730 lignes réellement mal taxées. La TVA légalement due excède le 445710 de 444,41 €','163, onglets « Étalons » et « Rappel autonome » ; 164'),
 ('3 Incidence reelle','F1','« TVA collectee reversee (compte 445710) »','TVA collectée comptabilisée (445710) sur les lignes « Total » ; TVA théorique par taux sur les autres lignes','tableau 46'),
 ('1 Semantique E et F, 2 Somme de la colonne F, 3 Incidence reelle','ensemble','cause des corrections de la colonne E non identifiée','la colonne 16 des annexes C porte le taux de l\'article de la ligne précédente (décalage d\'une ligne) ; 94,75 % des 32 047 lignes signalées sont des artefacts de ce décalage, et la colonne F mesure ces artefacts pour 102,9 % de son total','161 ; 164'),
 ('4 Controle par ticket','C2:F4','1 199 / 1 056 / 1 137 et 4 312 / 4 660 / 4 664 tickets (comparaison des TVA par taux)','les nombres cités par la section 2.5 portent sur l\'égalité des paliers TTC au centime : 1 147 / 1 018 / 1 095 (colonne 16), 4 312 / 4 664 / 4 675 (taux du service), 16 605 / 16 605 (taux appliqué)','tableau 56 ; 161, onglet « Paliers »'),
 ('5 Taux par article','B2:F4','dénombrements','valables (tableau 57)','tableau 57'),
 ('5 Taux par article','A6','« la colonne E corrige un defaut de l\'export, et non un parametrage de la caisse »','la colonne E part d\'un défaut de l\'export (décalage) ; cinq fiches articles sont en outre mal paramétrées (Pinte, Panaché, Monaco à 10 % ; 1 Boule Glace, Crêpe marron chantilly à 20 %), à taux constant','point 2.5.6 c ; 162'),
 ('6 Exemple 14-04-2022','A17','« la biere « La Vouivre » »','« La Vouivre » est un cocktail (Crémant du Jura, Macvin et crème de cassis, carte du 20/07/2021, p. 2)','tableau 49 ; 162, onglet « Sources »'),
 ('1 Semantique E et F, 6 Exemple 14-04-2022','A11, A17','« TVA reellement liquidee et reversee » ; « taxe encaissee »','TVA liquidée ; TVA comptabilisée','section 2.5 (vocabulaire)')])
E['88']=('88-R1-taux-tva-et-encaissements.xlsx','88-R3-taux-tva-par-article-et-lignes-signalees-erratum.xlsx',[
 ('TVA-1 Synthèse','F1, I1, J2:J5, L2:L5','« TVA supplémentaire due (+) » ; « TVA payée en trop (−) » ; incidence nette −9 424,74 € (−6,98 %)','qualification fausse : la colonne F du service mesure, pour 102,9 % de son total (−9 701,34 € sur −9 424,74 €), des artefacts du décalage d\'une ligne de la colonne 16. L\'incidence de l\'erreur de paramétrage est un effet de taux net de +647,21 € (TVA légalement due supérieure à la TVA liquidée)','162 ; 164'),
 ('TVA-2 Articles aux deux taux','ensemble','références présentes aux deux taux','taux de la colonne 16 décalée ; au taux appliqué par la caisse, aucune des 323 références n\'a deux taux','161, onglet « Références » ; tableau 57'),
 ('TVA-3 Relevé par article, TVA-4 Lignes signalées','G1 ; J1','« Incidence TVA (€) » par article et par ligne','valeur de la colonne F du service, non une incidence : 162 (onglets « Articles » et « Tickets ») remplace la pièce sur ce point','162'),
 ('Lecture','A13 à A15','la plupart des références apparaissent tantôt à 10 %, tantôt à 20 %','constat propre à la colonne 16 décalée ; au taux appliqué, chaque référence a un taux unique et cinq fiches sont mal paramétrées','161 ; 162'),
 ('ENC-4 Contrôle TVA caisse','B1','« TVA encaissée par la caisse »','TVA liquidée par la caisse (Σ tax_amount)','section 2.5 (vocabulaire)'),
 ('Ensemble de la pièce','','statut','erratum plutôt que nouvelle pièce : la pièce a été transmise et ses onglets TVA changent de nature ; les onglets ENC-1 à ENC-3 ne sont pas visés par la section 2.5','section 2.5')])
def make(desk,key):
    _,dst,rows=E[key]
    for r in rows:
        for t in r:
            assert '\u2014' not in t, t
    src=json.load(open(os.path.join(ICI,'cache','entrees.json'),encoding='utf-8'))[key]
    os.makedirs(DST,exist_ok=True); shutil.copy(src,DST+dst); os.chmod(DST+dst,0o644)
    doc=desk.loadComponentFromURL(uno.systemPathToFileUrl(DST+dst),'_blank',0,(pv('Hidden',True),))
    sh=doc.Sheets; sh.insertNewByName('Erratum R2',0); s=sh.getByName('Erratum R2')
    def put(r,c,t,bold=False):
        cl=s.getCellByPosition(c,r); cl.setString(t)
        cl.setPropertyValue('IsTextWrapped',True)
        if bold: cl.setPropertyValue('CharWeight',150.0)
    put(0,0,f'Pièce n° {key} : erratum R2 (classeur R3)',True); put(1,0,INTRO)
    for j,h in enumerate(H): put(3,j,h,True)
    for i,r in enumerate(rows):
        for j,t in enumerate(r): put(4+i,j,t)
    for j,wd in enumerate([4500,3500,7500,9500,5500]): s.getColumns().getByIndex(j).Width=wd
    if key=='38':
        for nm in ['3. Totaux mauvaise colonne','4. Totaux bonne colonne']:
            cl=sh.getByName(nm).getCellByPosition(5,0); assert cl.getFormula().replace(' ','').lower()=='=totalreconstitue', cl.getFormula(); cl.setString('= Total reconstitue')
    doc.calculateAll()
    doc.storeToURL(uno.systemPathToFileUrl(DST+dst),(pv('FilterName','Calc MS Excel 2007 XML'),)); doc.close(True)
    return DST+dst
def errata(*args):
    """Point d'entrée de la macro LibreOffice."""
    desk=XSCRIPTCONTEXT.getDesktop(); log=[]
    for k in ['38','85','86','87','88']: log.append('écrit '+make(desk,k))
    with open(os.path.join(ICI,'cache','log','b4_errata.txt'),'w',encoding='utf-8') as f: f.write('\n'.join(log)+'\n')
g_exportedScripts=(errata,)
if __name__=='__main__':
    sys.path.insert(0,ICI)
    from b4_recalc import connect
    d=connect()
    for k in ['38','85','86','87','88']: print('écrit',make(d,k))
    try: d.terminate()
    except Exception: pass
