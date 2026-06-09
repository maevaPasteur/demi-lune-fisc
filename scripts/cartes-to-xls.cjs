// Génère 3 .xls (Titre, Description, Quantité, Prix) à partir des cartes PDF
// vins & boissons. Une ligne par couple (produit, prix/volume).
// Données transcrites manuellement depuis pdftotext -layout.
const path = require('path')
const XLSX = require('xlsx')

const dir = path.join(__dirname, '..', 'public', 'documents', 'vins-boissons')
const HEADER = ['Titre', 'Description', 'Quantité', 'Prix']

// Raccourci : [titre, description, quantité, prix]
const r = (titre, description, quantite, prix) => [titre, description, quantite, prix]

// ============================================================================
// CARTE 08/02/2021
// ============================================================================
const carte_08 = [
  // --- Vins Rouges ---
  r('Arbois Trousseau', 'Domaine Jean-Louis Tissot - AOC. Vigne située sur Montigny les Arsures, la terre du Trousseau. Cépage arrivé dans le Jura vers le XVIIIe siècle. Vin léger et pourvu de tanins fins et mûrs.', 'Verre 15 cl', 6.4),
  r('Arbois Trousseau', 'Domaine Jean-Louis Tissot - AOC. Vigne située sur Montigny les Arsures, la terre du Trousseau. Cépage arrivé dans le Jura vers le XVIIIe siècle. Vin léger et pourvu de tanins fins et mûrs.', 'Bouteille 75 cl', 32),
  r('Saint Joseph', 'Domaine Stéphane Ogier - AOP. Le vignoble de Saint-Joseph s’étend sur la rive droite du Rhône. Il est planté sur des coteaux abrupts, façonnés en terrasses depuis l’antiquité. Appellation connue pour ses vins rouges issus de Syrah, à la fois puissants et fins.', 'Verre 15 cl', 7.2),
  r('Saint Joseph', 'Domaine Stéphane Ogier - AOP. Le vignoble de Saint-Joseph s’étend sur la rive droite du Rhône. Il est planté sur des coteaux abrupts, façonnés en terrasses depuis l’antiquité. Appellation connue pour ses vins rouges issus de Syrah, à la fois puissants et fins.', 'Bouteille 75 cl', 36),
  r('Moulin à Vent', 'Domaine Jambon à Saint-Lager près de la Chapelle de Brouilly - AOP. Cépage : Gamay. Vin d’une couleur intense, à la robe oscillante entre un grenat sombre et un rubis profond. Tannique et charnu.', 'Verre 15 cl', 5.8),
  r('Moulin à Vent', 'Domaine Jambon à Saint-Lager près de la Chapelle de Brouilly - AOP. Cépage : Gamay. Vin d’une couleur intense, à la robe oscillante entre un grenat sombre et un rubis profond. Tannique et charnu.', 'Bouteille 75 cl', 29),
  r('Hautes Côtes de Nuits', 'Domaine Bouchard Père & Fils, Beaune - AOC. Cépage : Pinot noir. Bouquet dévoilant des parfums de baies rouges et noires. Il exprime ses arômes sur une structure ferme qui souligne sa franchise.', 'Verre 15 cl', 7.9),
  r('Hautes Côtes de Nuits', 'Domaine Bouchard Père & Fils, Beaune - AOC. Cépage : Pinot noir. Bouquet dévoilant des parfums de baies rouges et noires. Il exprime ses arômes sur une structure ferme qui souligne sa franchise.', 'Bouteille 75 cl', 39.5),
  r('Mouton Cadet', 'Baron Philippe de Rothschild - AOC. Sa robe de couleur cerise noire, intense et brillante dévoile un nez dense et raffiné. En bouche, ses tanins puissants et sa texture ample et onctueuse proposent un équilibre général remarquable. La finale, légèrement épicée, est généreuse et agréable. 86 % Merlot, 10 % Cabernet-sauvignon, 4 % Cabernet-franc.', 'Bouteille 75 cl', 36),
  // --- Vins Blancs ---
  r('Arbois Chardonnay', 'Domaine Jean Louis Tissot à Montigny-lès-Arsures - AOC.', 'Bouteille 75 cl', 24.9),
  r('Arbois Cuvée Béthanie', 'Fruitière Vinicole d’Arbois - AOC. Très typé jurassien avec ses 60 % de Chardonnay et 40 % de Savagnin.', 'Bouteille 37,5 cl', 19),
  r('Arbois Cuvée Béthanie', 'Fruitière Vinicole d’Arbois - AOC. Très typé jurassien avec ses 60 % de Chardonnay et 40 % de Savagnin.', 'Bouteille 75 cl', 29.9),
  r('Arbois Savagnin', 'Fruitière Vinicole d’Arbois - AOC. Avec des arômes puissants de noix, de vanille et d’amandes grillées, ce grand vin tutoie son illustre parent, le vin jaune. Notre Savagnin s’exprime sur des tonalités complexes typiques du terroir jurassien.', 'Verre 15 cl', 7.2),
  r('Arbois Savagnin', 'Fruitière Vinicole d’Arbois - AOC. Avec des arômes puissants de noix, de vanille et d’amandes grillées, ce grand vin tutoie son illustre parent, le vin jaune. Notre Savagnin s’exprime sur des tonalités complexes typiques du terroir jurassien.', 'Bouteille 75 cl', 36),
  r('Saint Véran', 'Domaine du Paradis - AOP. Chardonnay du vignoble Mâconnais.', 'Verre 15 cl', 7.9),
  r('Saint Véran', 'Domaine du Paradis - AOP. Chardonnay du vignoble Mâconnais.', 'Bouteille 75 cl', 39.5),
  r('Hautes Côtes de Nuits', 'Domaine Lupé-Cholet à Nuits-Saint-Georges - AOP. Chardonnay du vignoble de Bourgogne situé sur les coteaux juste derrière la Côte de Nuits (à l’ouest).', 'Verre 15 cl', 7.9),
  r('Hautes Côtes de Nuits', 'Domaine Lupé-Cholet à Nuits-Saint-Georges - AOP. Chardonnay du vignoble de Bourgogne situé sur les coteaux juste derrière la Côte de Nuits (à l’ouest).', 'Bouteille 75 cl', 39.5),
  r('Gewurztraminer', 'Château de Riquewihr “Les Sorcières”, Domaine Dopff et Irion - AOC. Vin doux, à l’attaque épicée, milieu de bouche moelleux.', 'Verre 15 cl', 7),
  r('Gewurztraminer', 'Château de Riquewihr “Les Sorcières”, Domaine Dopff et Irion - AOC. Vin doux, à l’attaque épicée, milieu de bouche moelleux.', 'Bouteille 75 cl', 35),
  // --- Vins Rosés ---
  r('Clair de Rosé', 'Les Jamelles à Monze, au pied de la Montagne d’Alaric - IGP Pays d’Oc. Assemblage de deux cépages, le Grenache et le Cinsault.', 'Bouteille 75 cl', 18),
  r('Miraval', 'Côtes de Provence - AOP. La cuvée phare de Brad Pitt, vinifiée par la famille Perrin, star de la vallée du Rhône. Élu meilleur rosé du monde par Wine Spectator, le rosé le plus « people » ! Miraval rosé provient des meilleures vignes du château, bénéficiant de sa propre vallée au cœur de la Provence.', 'Bouteille 75 cl', 45),
  // --- Pichets ---
  r('Bourgogne Aligoté', 'Pichet — Blanc. AOC.', 'Verre 15 cl', 3.9),
  r('Bourgogne Aligoté', 'Pichet — Blanc. AOC.', 'Pichet 50 cl', 9.9),
  r('Bourgogne Aligoté', 'Pichet — Blanc. AOC.', 'Pichet 75 cl', 13.9),
  r('Côtes du Rhône “Enclave des Papes”', 'Pichet — Rouge. AOC.', 'Verre 15 cl', 3.9),
  r('Côtes du Rhône “Enclave des Papes”', 'Pichet — Rouge. AOC.', 'Pichet 50 cl', 9.9),
  r('Côtes du Rhône “Enclave des Papes”', 'Pichet — Rouge. AOC.', 'Pichet 75 cl', 13.9),
  r('Côtes de Provence “Cap des Pins”', 'Pichet — Rosé. Maîtres Vignerons de la Presqu’île de St Tropez - IGP.', 'Verre 15 cl', 3.9),
  r('Côtes de Provence “Cap des Pins”', 'Pichet — Rosé. Maîtres Vignerons de la Presqu’île de St Tropez - IGP.', 'Pichet 50 cl', 9.9),
  r('Côtes de Provence “Cap des Pins”', 'Pichet — Rosé. Maîtres Vignerons de la Presqu’île de St Tropez - IGP.', 'Pichet 75 cl', 13.9),
  // --- Apéritifs Maison ---
  r('La Vouivre', 'Crémant du Jura, Macvin et Crème de Cassis.', '12 cl', 5.2),
  r('Apéritif du Père Grégoire', 'Macvin et Liqueur de Cerise.', '6 cl', 4.9),
  r('Chat Perché', 'Macvin, Jus de Poire et Sirop de Châtaigne.', '12 cl', 5.2),
  r('Kittykir', 'Soho “Liqueur de Litchi”, Crémant du Jura et Sirop de Framboise.', '12 cl', 5.2),
  // --- Spécialités Régionales ---
  r('Macvin', 'Le macvin du Jura est un vin de liqueur, produit de l’assemblage de moût et d’eau-de-vie de marc du Jura.', '6 cl', 4.9),
  r('Vin de Paille', 'Vin naturellement doux élaboré sans ajout d’alcool, moelleux ou liquoreux de couleur ambrée, obtenu par pressurage et fermentation de raisins passerillés sur des claies, autrefois de paille d’où le nom du vin.', '6 cl', 6),
  r('Vin Jaune', 'Élevé pendant six ans et trois mois dans les caves jurassiennes. Vin blanc sec issu exclusivement du cépage local, le savagnin. Robe dorée, arômes de noix fraîche, fruits secs et épices douces. Bouche riche et puissante.', '12 cl', 12),
  r('Pontarlier', 'Apéritif alcoolisé à base d’anis vert confectionné dans la région de Pontarlier en Franche-Comté.', '2 cl', 3.8),
  // --- Apéritifs sans alcool ---
  r('Mambo', 'Jus d’Orange et Jus de Fraise et Limonade “La Mortuacienne”.', '25 cl', 6.5),
  r('Luna', 'Jus de Poire, Limonade “La Mortuacienne” et sirop de Châtaigne.', '25 cl', 6),
  // --- Autres Apéritifs ---
  r('Pastis ou Ricard', '', '2 cl', 3.8),
  r('Porto Rouge ou Martini Blanc', '', '6 cl', 3.8),
  r('Kir', 'Bourgogne blanc Aligoté et crème de Cassis.', '12 cl', 3.8),
  r('Rosé “Pamp”', 'Côtes de Provence “Saint Tropez” et sirop de Pamplemousse.', '12 cl', 3.8),
  r('Whisky “Long John”', '', 'Baby 2 cl', 3.8),
  r('Whisky “Long John”', '', 'Verre 4 cl', 5.8),
  r('Whisky “Long John”', '', 'Verre 4 cl + Coca-Cola', 7.5),
  r('Whisky “Jack Daniel’s”', '', '4 cl', 7.5),
  // --- Cocktails ---
  r('Tequila sunrise', '4 cl Tequila, Jus d’Orange et sirop de Grenadine.', '25 cl', 7.5),
  r('Balidou', '4 cl Passoä “Fruits de la Passion”, Jus d’Ananas et sirop Framboise.', '25 cl', 7.5),
  r('Rêve Bleu', '4 cl Vodka, Jus de Pomme et sirop de Curaçao Bleu.', '25 cl', 7.5),
  r('Maëva', '4 cl de Soho “liqueur de Litchi”, 4 cl de Vodka et Jus de Framboise.', '25 cl', 7.5),
  r('Rabasse', '2 cl Pontarlier, 2 cl Liqueur de Sapin et Limonade artisanale.', '25 cl', 7.5),
  // --- Bières ---
  r('Pression Affligem', 'Bière blonde d’abbaye Belge.', '25 cl', 3.9),
  r('Pression Affligem', 'Bière blonde d’abbaye Belge.', '50 cl', 7.8),
  r('Panaché', 'Bière + Limonade.', '25 cl', 3.9),
  r('Panaché', 'Bière + Limonade.', '50 cl', 7.8),
  r('Picon Bière', '', '25 cl', 4.5),
  r('Picon Bière', '', '50 cl', 8.9),
  r('Rouget de Lisle', 'Brasserie artisanale jurassienne située à Bletterans. “Blanche des Plateaux” ou “Ambrée”.', 'Bouteille 33 cl', 5.9),
  // --- Boissons sans alcool ---
  r('Limonade artisanale F-Comtoise “La Mortuacienne”', '', '25 cl', 3.9),
  r('Soda au choix', 'Coca-Cola, Schweppes Agrum’, Orangina, Fuze Tea ou Fanta Citron.', '25 cl', 3.9),
  r('Jus de Fruits au choix', 'Orange, Pomme, Poire, Ananas, Raisin, Fraise, Framboise ou Tomate.', '20 cl', 3.9),
  r('Sirop à l’eau', 'Fraise, Menthe, Orange, Citron, Framboise, Pêche, Orgeat, Grenadine, Pamplemousse ou Châtaigne.', '25 cl', 14),
  // --- Eaux minérales ---
  r('Perrier', 'Bouteille.', 'Bouteille 33 cl', 4),
  r('Vittel ou San Pellegrino', '', '50 cl', 4),
  r('Vittel ou San Pellegrino', '', '1 L', 5.9),
]

// ============================================================================
// CARTE 20/07/2021
// ============================================================================
const APMACVIN = 'Le macvin du Jura est un vin de liqueur, produit de l’assemblage de moût et d’eau-de-vie de marc du Jura.'
const APPAILLE = 'Vin naturellement doux élaboré sans ajout d’alcool, moelleux ou liquoreux de couleur ambrée, obtenu par pressurage et fermentation de raisins passerillés sur des claies, autrefois de paille d’où le nom du vin.'
const APJAUNE = 'Élevé pendant six ans et trois mois dans les caves jurassiennes. Vin blanc sec issu exclusivement du cépage local, le savagnin. Robe dorée, arômes de noix fraîche, fruits secs et épices douces. Bouche riche et puissante.'
const APPONT = 'Apéritif alcoolisé à base d’anis vert confectionné dans la région de Pontarlier en Franche-Comté.'

const carte_20 = [
  // --- Apéritifs Maison ---
  r('La Vouivre', 'Crémant du Jura, Macvin et Crème de Cassis.', '12 cl', 5.9),
  r('Apéritif du Père Grégoire', 'Crémant du Jura, Macvin et Liqueur cerise.', '6 cl', 5.9),
  r('Chat Perché', 'Macvin, Jus de Poire et Sirop de Châtaigne.', '12 cl', 5.9),
  r('Kittykir', 'Soho “Liqueur de Litchi”, Crémant du Jura et Sirop de Framboise.', '12 cl', 5.9),
  // --- Spécialités Régionales ---
  r('Macvin', APMACVIN, '6 cl', 5.9),
  r('Vin de Paille', APPAILLE, '6 cl', 6.9),
  r('Vin Jaune', APJAUNE, '12 cl', 12),
  r('Pontarlier', APPONT, '2 cl', 4.2),
  // --- Apéritifs sans alcool ---
  r('Mambo', 'Jus d’Orange et Jus de Fraise et Limonade “La Mortuacienne”.', '25 cl', 6.5),
  r('Luna', 'Jus de Poire, Limonade “La Mortuacienne” et sirop de Châtaigne.', '25 cl', 6),
  // --- Cocktails ---
  r('Spritz jurassien', '4 cl Aperol, Crémant du Jura et Perrier.', '', 9),
  r('Balidou', '4 cl Passoä “Fruits de la Passion”, Jus d’Ananas et sirop Framboise.', '', 9),
  r('Rêve Bleu', '4 cl Vodka, Jus de Pomme et sirop de Curaçao Bleu.', '', 9),
  r('Maëva', '4 cl de Soho “liqueur de Litchi”, 4 cl de Vodka et Jus de Framboise.', '', 9),
  r('Rabasse', '2 cl Pontarlier, 2 cl Liqueur de Sapin et Limonade artisanale.', '', 9),
  // --- Autres Apéritifs ---
  r('Pastis ou Ricard', '', '2 cl', 4.2),
  r('Porto Rouge ou Martini Blanc', '', '6 cl', 4.9),
  r('Kir', 'Bourgogne blanc Aligoté et crème de Cassis.', '12 cl', 4.2),
  r('Whisky Clan Campbell', '', 'Baby 2 cl', 3.2),
  r('Whisky Clan Campbell', '', 'Verre 4 cl', 6.9),
  r('Whisky Clan Campbell', '', 'Verre 4 cl + Coca-Cola', 9),
  r('Whisky “Jack Daniel’s”', '', '4 cl', 7.5),
  // --- Bières ---
  r('Pression Affligem', 'Bière blonde d’abbaye Belge.', '25 cl', 4.2),
  r('Pression Affligem', 'Bière blonde d’abbaye Belge.', '50 cl', 8),
  r('Panaché Bière + Limonade', '', '25 cl', 4.2),
  r('Panaché Bière + Limonade', '', '50 cl', 8),
  r('Picon Bière', '', '25 cl', 4.8),
  r('Picon Bière', '', '50 cl', 9),
  r('Rouget de Lisle', 'Brasserie artisanale jurassienne située à Bletterans. “Blanche des Plateaux” ou “Ambrée”.', 'Bouteille 33 cl', 6.9),
  // --- Boissons sans alcool ---
  r('Limonade artisanale F-Comtoise “La Mortuacienne”', '', '25 cl', 3.9),
  r('Soda au choix', 'Coca-Cola, Schweppes Agrum’, Orangina, Fuze Tea ou Fanta Citron.', '33 cl', 3.9),
  r('Jus de Fruits au choix', 'Orange, Pomme, Poire, Ananas, Raisin, Fraise, Framboise ou Tomate.', '25 cl', 4.2),
  r('Sirop à l’eau', 'Fraise, Menthe, Orange, Citron, Framboise, Pêche, Orgeat, Grenadine, Pamplemousse ou Châtaigne.', '25 cl', 2.2),
  // --- Eaux minérales ---
  r('Perrier', 'Bouteille.', 'Bouteille 33 cl', 4),
  r('Vittel ou San Pellegrino', '', '50 cl', 4),
  r('Vittel ou San Pellegrino', '', '1 L', 5.9),
  // --- Vins Rouges ---
  r('Côtes-du-Rhône rouge', 'Cave des vignerons de Chusclan - AOC.', 'Verre 15 cl', 3.9),
  r('Côtes-du-Rhône rouge', 'Cave des vignerons de Chusclan - AOC.', 'Pichet 50 cl', 9.5),
  r('Arbois Trousseau', 'Domaine Jean-Louis Tissot - AOC. Vigne située sur Montigny les Arsures, la terre du Trousseau. Cépage arrivé dans le Jura vers le XVIIIe siècle. Vin léger et pourvu de tanins fins et mûrs.', 'Verre 15 cl', 7.2),
  r('Arbois Trousseau', 'Domaine Jean-Louis Tissot - AOC. Vigne située sur Montigny les Arsures, la terre du Trousseau. Cépage arrivé dans le Jura vers le XVIIIe siècle. Vin léger et pourvu de tanins fins et mûrs.', 'Pichet 50 cl', 28),
  r('Arbois Trousseau', 'Domaine Jean-Louis Tissot - AOC. Vigne située sur Montigny les Arsures, la terre du Trousseau. Cépage arrivé dans le Jura vers le XVIIIe siècle. Vin léger et pourvu de tanins fins et mûrs.', 'Bouteille 75 cl', 36),
  r('Saint Joseph', 'Domaine Ogier - AOC. Le vignoble de Saint-Joseph s’étend sur la rive droite du Rhône. Il est planté sur des coteaux abrupts, façonnés en terrasses depuis l’antiquité. Appellation connue pour ses vins rouges issus de Syrah, à la fois puissants et fins.', 'Verre 15 cl', 9.7),
  r('Saint Joseph', 'Domaine Ogier - AOC. Le vignoble de Saint-Joseph s’étend sur la rive droite du Rhône. Il est planté sur des coteaux abrupts, façonnés en terrasses depuis l’antiquité. Appellation connue pour ses vins rouges issus de Syrah, à la fois puissants et fins.', 'Pichet 50 cl', 32.2),
  r('Saint Joseph', 'Domaine Ogier - AOC. Le vignoble de Saint-Joseph s’étend sur la rive droite du Rhône. Il est planté sur des coteaux abrupts, façonnés en terrasses depuis l’antiquité. Appellation connue pour ses vins rouges issus de Syrah, à la fois puissants et fins.', 'Bouteille 75 cl', 48.5),
  r('Moulin à Vent', 'Domaine de Briante - AOC. Vous retrouvez dans cette cuvée les qualités peu connues du gamay telle la complexité, la souplesse aromatiques (fleurs, violette) dans les premières années, empruntant ensuite des notes plus charnues. Charpenté et complexe, le Moulin-à-vent est le vin de garde par excellence.', 'Verre 15 cl', 7.6),
  r('Moulin à Vent', 'Domaine de Briante - AOC. Vous retrouvez dans cette cuvée les qualités peu connues du gamay telle la complexité, la souplesse aromatiques (fleurs, violette) dans les premières années, empruntant ensuite des notes plus charnues. Charpenté et complexe, le Moulin-à-vent est le vin de garde par excellence.', 'Pichet 50 cl', 26),
  r('Moulin à Vent', 'Domaine de Briante - AOC. Vous retrouvez dans cette cuvée les qualités peu connues du gamay telle la complexité, la souplesse aromatiques (fleurs, violette) dans les premières années, empruntant ensuite des notes plus charnues. Charpenté et complexe, le Moulin-à-vent est le vin de garde par excellence.', 'Bouteille 75 cl', 38),
  r('Hautes Côtes de Beaune', 'Domaine Germain - AOC. Vin fruité et fin, aux notes de sous-bois, de petits fruits rouges frais (fraise, framboise) et très floral. Il accompagnera parfaitement une viande blanche (volaille, veau) ou se dégustera simplement en apéritif.', 'Verre 15 cl', 9.5),
  r('Hautes Côtes de Beaune', 'Domaine Germain - AOC. Vin fruité et fin, aux notes de sous-bois, de petits fruits rouges frais (fraise, framboise) et très floral. Il accompagnera parfaitement une viande blanche (volaille, veau) ou se dégustera simplement en apéritif.', 'Pichet 50 cl', 32),
  r('Hautes Côtes de Beaune', 'Domaine Germain - AOC. Vin fruité et fin, aux notes de sous-bois, de petits fruits rouges frais (fraise, framboise) et très floral. Il accompagnera parfaitement une viande blanche (volaille, veau) ou se dégustera simplement en apéritif.', 'Bouteille 75 cl', 49),
  r('La Côte rouge', 'Château la Negly - AOP La Clape. Robe rubis, arômes de cassis et de poivre noir et notes de réglisse. À déguster sur volailles, viandes rouges et fromages. Cépages : carignan, syrah et grenache.', 'Bouteille 75 cl', 29),
  // --- Vins Blancs ---
  r('Bourgogne Aligoté', 'Cave de Buxy - AOC.', 'Verre 15 cl', 3.9),
  r('Bourgogne Aligoté', 'Cave de Buxy - AOC.', 'Pichet 50 cl', 10.5),
  r('Arbois Cuvée Béthanie', 'Fruitière Vinicole d’Arbois - AOC. Très typé jurassien avec ses 60 % de Chardonnay et 40 % de Savagnin.', 'Bouteille 37,5 cl', 24),
  r('Arbois Cuvée Béthanie', 'Fruitière Vinicole d’Arbois - AOC. Très typé jurassien avec ses 60 % de Chardonnay et 40 % de Savagnin.', 'Bouteille 75 cl', 36),
  r('Arbois Chardonnay', 'Domaine Jean Louis Tissot à Montigny-lès-Arsures - AOC.', 'Bouteille 75 cl', 29),
  r('Arbois Savagnin', 'Fruitière Vinicole d’Arbois - AOC. Avec des arômes puissants de noix, de vanille et d’amandes grillées, ce grand vin tutoie son illustre parent, le vin jaune. Notre Savagnin s’exprime sur des tonalités complexes typiques du terroir jurassien.', 'Verre 15 cl', 8.3),
  r('Arbois Savagnin', 'Fruitière Vinicole d’Arbois - AOC. Avec des arômes puissants de noix, de vanille et d’amandes grillées, ce grand vin tutoie son illustre parent, le vin jaune. Notre Savagnin s’exprime sur des tonalités complexes typiques du terroir jurassien.', 'Pichet 50 cl', 28),
  r('Arbois Savagnin', 'Fruitière Vinicole d’Arbois - AOC. Avec des arômes puissants de noix, de vanille et d’amandes grillées, ce grand vin tutoie son illustre parent, le vin jaune. Notre Savagnin s’exprime sur des tonalités complexes typiques du terroir jurassien.', 'Bouteille 75 cl', 41.5),
  r('Saint Véran', 'Domaine du Paradis - AOP. Chardonnay du vignoble Mâconnais.', 'Verre 15 cl', 7.9),
  r('Saint Véran', 'Domaine du Paradis - AOP. Chardonnay du vignoble Mâconnais.', 'Pichet 50 cl', 30),
  r('Saint Véran', 'Domaine du Paradis - AOP. Chardonnay du vignoble Mâconnais.', 'Bouteille 75 cl', 39.5),
  r('Mâcon Roche blanche', 'Domaine Mathias - AOC Bio, situé à Chaintré à côté de Mâcon. Vin 100 % chardonnay aux arômes d’agrumes et de fruits à chair blanche.', 'Verre 15 cl', 6.3),
  r('Mâcon Roche blanche', 'Domaine Mathias - AOC Bio, situé à Chaintré à côté de Mâcon. Vin 100 % chardonnay aux arômes d’agrumes et de fruits à chair blanche.', 'Pichet 50 cl', 21),
  r('Mâcon Roche blanche', 'Domaine Mathias - AOC Bio, situé à Chaintré à côté de Mâcon. Vin 100 % chardonnay aux arômes d’agrumes et de fruits à chair blanche.', 'Bouteille 75 cl', 31),
  r('Chablis St Martin', 'Domaine Laroche - AOC. Grâce à un élevage rigoureux sur lies fines, offre la minéralité caractéristique des meilleurs terroirs de l’appellation.', 'Bouteille 75 cl', 47),
  r('Gewurztraminer', 'Château de Riquewihr “Les Sorcières”, Domaine Dopff et Irion - AOC. Vin doux, à l’attaque épicée, milieu de bouche moelleux.', 'Verre 15 cl', 7),
  r('Gewurztraminer', 'Château de Riquewihr “Les Sorcières”, Domaine Dopff et Irion - AOC. Vin doux, à l’attaque épicée, milieu de bouche moelleux.', 'Pichet 50 cl', 27),
  r('Gewurztraminer', 'Château de Riquewihr “Les Sorcières”, Domaine Dopff et Irion - AOC. Vin doux, à l’attaque épicée, milieu de bouche moelleux.', 'Bouteille 75 cl', 35),
  r('Côtes de Gascogne', 'Domaine Haut Marin - Grand Pavois N° 8 - IGP. Vignoble situé en plein cœur du bas Armagnac. Assemblage de petit et gros manseng, parfait équilibre entre la sucrosité et la fraîcheur des fruits exotiques.', 'Bouteille 75 cl', 22),
  // --- Vins Rosés ---
  r('Côtes-de-Provence', 'Cap des Pins, vignerons de St. Tropez - AOC.', 'Verre 15 cl', 3.9),
  r('Côtes-de-Provence', 'Cap des Pins, vignerons de St. Tropez - AOC.', 'Pichet 50 cl', 10.5),
  r('Côtes-de-Provence', 'Château Minuty - AOC. Situé sur la presqu’île de St Tropez, le vin se compose de syrah et de cinsault. Notes d’écorces d’orange et de groseilles.', 'Bouteille 75 cl', 45),
  r('Clair de Rosé', 'Les Jamelles à Monze, au pied de la Montagne d’Alaric - IGP Pays d’Oc. Assemblage de deux cépages, le Grenache et le Cinsault.', 'Bouteille 75 cl', 19.6),
  r('Domaine Le Pive Bio', 'IGP Sable de Camargue. Explosion de notes fraîches de fraises et d’agrumes, notes de bonbons anglais.', 'Bouteille 75 cl', 29),
  // --- Pétillants ---
  r('Crémant du Jura Blanc Brut', 'Maison Tissot, Montigny les Arsures - AOP. À majorité de Chardonnay, bulles fines, intenses et légères, arômes fruités et floraux typiques de son cépage.', 'Verre 12 cl', 5),
  r('Crémant du Jura Blanc Brut', 'Maison Tissot, Montigny les Arsures - AOP. À majorité de Chardonnay, bulles fines, intenses et légères, arômes fruités et floraux typiques de son cépage.', 'Bouteille 75 cl', 29),
  r('Cidre Breton “La Bolée d’Armorique” Brut', 'AOC.', 'Bouteille 75 cl', 16),
  r('Cidre Normand Contemporaine Doux', 'AOC.', 'Bouteille 75 cl', 16),
  r('Cidre La Mordue “Hard Cider”', 'À la fois fruitée, acidulée et pétillante, sans amertume. Fabriquée en France avec des pommes françaises (Coopérative Agrial) ; fermentation courte et dirigée où tout le sucre est transformé en alcool.', 'Bouteille 27,5 cl', 4.8),
  // --- Digestifs (Verre 4 cl) ---
  r('Liqueur de Bourgeons de Sapin du Haut-Doubs 40°', '', 'Verre 4 cl', 6.5),
  r('Liqueur de Génépi 42°', 'Distillerie les fils d’Émile Pernot à La Cluse et Mijoux.', 'Verre 4 cl', 6.5),
  r('Eau de Vie de Poire Williams 45°', 'Distillerie Peureux à Fougerolles.', 'Verre 4 cl', 6.5),
  r('Eau de Vie de Mirabelle ou Framboise 45°', 'Distillerie Michel à Chapelle des Bois.', 'Verre 4 cl', 6.5),
  r('Vieux Marc de Bourgogne 40°', '', 'Verre 4 cl', 6.5),
  r('Marc du Jura 40°', 'Domaine Tissot.', 'Verre 4 cl', 6.5),
  r('Liqueur de Poire Golden Eight 25°', 'Distillerie Peureux à Fougerolles.', 'Verre 4 cl', 6.5),
  r('Get 27 21°', 'Liqueur de Menthe.', 'Verre 4 cl', 6.5),
  r('Get 31 24°', 'Liqueur de menthe poivrée.', 'Verre 4 cl', 6.5),
  r('Grand Marnier 40°', 'Liqueur à base de Cognac et d’oranges.', 'Verre 4 cl', 6.5),
  r('Cognac 40°', 'Eau-de-vie de vin.', 'Verre 4 cl', 6.5),
  r('Calvados Beaujour 40°', 'Distillerie Busnel.', 'Verre 4 cl', 6.9),
  r('Baileys', '', 'Verre 4 cl', 6.5),
  // --- Boissons chaudes ---
  r('Expresso', '', '', 2.2),
  r('Expresso Crème', '', '', 2.4),
  r('Thé, Infusion', '', '', 3.4),
  r('Double Expresso', '', '', 3.8),
  r('Double Expresso', '', '', 4.2),
  r('Café Viennois', 'Double expresso, chantilly.', '', 5.5),
  r('Café Irlandais', 'Double expresso, 4 cl de whisky, chantilly.', '', 9),
]

// ============================================================================
// CARTE 26/04/2023 (aujourd’hui)
// ============================================================================
const carte_26 = [
  // --- Apéritifs Maison ---
  r('La Vouivre', 'Crémant du Jura, Macvin et Crème de Cassis.', '12 cl', 5.2),
  r('Apéritif du Père Grégoire', 'Crémant du Jura, Macvin et Liqueur cerise.', '6 cl', 4.9),
  r('Chat Perché', 'Macvin, Jus de Poire et Sirop de Châtaigne.', '12 cl', 5.2),
  r('Kittykir', 'Soho “Liqueur de Litchi”, Crémant du Jura et Sirop de Framboise.', '12 cl', 5.2),
  // --- Spécialités Régionales ---
  r('Macvin', APMACVIN, '6 cl', 4.9),
  r('Vin de Paille', APPAILLE, '6 cl', 6),
  r('Vin Jaune', APJAUNE, '12 cl', 12),
  r('Pontarlier', APPONT, '2 cl', 3.8),
  // --- Apéritifs sans alcool ---
  r('Mambo', 'Jus d’Orange et Jus de Fraise et Limonade “La Mortuacienne”.', '25 cl', 6.5),
  r('Luna', 'Jus de Poire, Limonade “La Mortuacienne” et sirop de Châtaigne.', '25 cl', 6),
  // --- Autres Apéritifs ---
  r('Pastis ou Ricard', '', '2 cl', 3.8),
  r('Porto Rouge ou Martini Blanc', '', '6 cl', 3.8),
  r('Kir', 'Bourgogne blanc Aligoté et crème de Cassis.', '12 cl', 3.8),
  r('Rosé “Pamp”', 'Côtes de Provence “Saint Tropez” et sirop de Pamplemousse.', '12 cl', 3.8),
  r('Whisky Clan Campbell', '', 'Baby 2 cl', 3.8),
  r('Whisky Clan Campbell', '', 'Verre 4 cl', 5.8),
  r('Whisky Clan Campbell', '', 'Verre 4 cl + Coca-Cola', 7.5),
  r('Whisky “Jack Daniel’s”', '', '4 cl', 7.5),
  // --- Cocktails ---
  r('Tequila sunrise', '4 cl Tequila, Jus d’Orange et sirop de Grenadine.', '', 9),
  r('Balidou', '4 cl Passoä “Fruits de la Passion”, Jus d’Ananas et sirop Framboise.', '', 9),
  r('Rêve Bleu', '4 cl Vodka, Jus de Pomme et sirop de Curaçao Bleu.', '', 9),
  r('Maëva', '4 cl de Soho “liqueur de Litchi”, 4 cl de Vodka et Jus de Framboise.', '', 9),
  r('Rabasse', '2 cl Pontarlier, 2 cl Liqueur de Sapin et Limonade artisanale.', '', 9),
  // --- Bières ---
  r('Pression Affligem', 'Bière blonde d’abbaye Belge.', '25 cl', 3.9),
  r('Pression Affligem', 'Bière blonde d’abbaye Belge.', '50 cl', 7.8),
  r('Panaché Bière + Limonade', '', '25 cl', 3.9),
  r('Panaché Bière + Limonade', '', '50 cl', 7.8),
  r('Picon Bière', '', '25 cl', 4.5),
  r('Picon Bière', '', '50 cl', 8.9),
  r('Rouget de Lisle', 'Brasserie artisanale jurassienne située à Bletterans. “Blanche des Plateaux” ou “Ambrée”.', 'Bouteille 33 cl', 5.9),
  // --- Boissons sans alcool ---
  r('Limonade artisanale F-Comtoise “La Mortuacienne”', '', '25 cl', 3.9),
  r('Soda au choix', 'Coca-Cola, Schweppes Agrum’, Orangina, Fuze Tea ou Fanta Citron.', '33 cl', 3.9),
  r('Jus de Fruits au choix', 'Orange, Pomme, Poire, Ananas, Raisin, Fraise, Framboise ou Tomate.', '25 cl', 3.9),
  r('Sirop à l’eau', 'Fraise, Menthe, Orange, Citron, Framboise, Pêche, Orgeat, Grenadine, Pamplemousse ou Châtaigne.', '25 cl', 2.2),
  // --- Eaux minérales ---
  r('Perrier', 'Bouteille.', 'Bouteille 33 cl', 4),
  r('Vittel ou San Pellegrino', '', '50 cl', 4),
  r('Vittel ou San Pellegrino', '', '1 L', 5.9),
  // --- Vins Rouges ---
  r('Arbois Trousseau', 'Domaine Jean-Louis Tissot - AOC. Vigne située sur Montigny les Arsures, la terre du Trousseau. Cépage arrivé dans le Jura vers le XVIIIe siècle. Vin léger et pourvu de tanins fins et mûrs.', 'Verre 15 cl', 6.4),
  r('Arbois Trousseau', 'Domaine Jean-Louis Tissot - AOC. Vigne située sur Montigny les Arsures, la terre du Trousseau. Cépage arrivé dans le Jura vers le XVIIIe siècle. Vin léger et pourvu de tanins fins et mûrs.', 'Pichet 50 cl', 24),
  r('Arbois Trousseau', 'Domaine Jean-Louis Tissot - AOC. Vigne située sur Montigny les Arsures, la terre du Trousseau. Cépage arrivé dans le Jura vers le XVIIIe siècle. Vin léger et pourvu de tanins fins et mûrs.', 'Bouteille 75 cl', 32),
  r('Saint Joseph', 'Domaine Ogier - AOP. Le vignoble de Saint-Joseph s’étend sur la rive droite du Rhône. Il est planté sur des coteaux abrupts, façonnés en terrasses depuis l’antiquité. Appellation connue pour ses vins rouges issus de Syrah, à la fois puissants et fins.', 'Verre 15 cl', 7.2),
  r('Saint Joseph', 'Domaine Ogier - AOP. Le vignoble de Saint-Joseph s’étend sur la rive droite du Rhône. Il est planté sur des coteaux abrupts, façonnés en terrasses depuis l’antiquité. Appellation connue pour ses vins rouges issus de Syrah, à la fois puissants et fins.', 'Pichet 50 cl', 28),
  r('Saint Joseph', 'Domaine Ogier - AOP. Le vignoble de Saint-Joseph s’étend sur la rive droite du Rhône. Il est planté sur des coteaux abrupts, façonnés en terrasses depuis l’antiquité. Appellation connue pour ses vins rouges issus de Syrah, à la fois puissants et fins.', 'Bouteille 75 cl', 36),
  r('Moulin à Vent', 'Domaine de Briante. Vous retrouvez dans cette cuvée les qualités peu connues du gamay telle la complexité, la souplesse aromatiques (fleurs, violette) dans les premières années, empruntant ensuite des notes plus charnues. Charpenté et complexe, le Moulin-à-vent est le vin de garde par excellence.', 'Verre 15 cl', 5.8),
  r('Moulin à Vent', 'Domaine de Briante. Vous retrouvez dans cette cuvée les qualités peu connues du gamay telle la complexité, la souplesse aromatiques (fleurs, violette) dans les premières années, empruntant ensuite des notes plus charnues. Charpenté et complexe, le Moulin-à-vent est le vin de garde par excellence.', 'Pichet 50 cl', 21),
  r('Moulin à Vent', 'Domaine de Briante. Vous retrouvez dans cette cuvée les qualités peu connues du gamay telle la complexité, la souplesse aromatiques (fleurs, violette) dans les premières années, empruntant ensuite des notes plus charnues. Charpenté et complexe, le Moulin-à-vent est le vin de garde par excellence.', 'Bouteille 75 cl', 29),
  r('Hautes Côtes de Beaune', 'Domaine Germain. Vin fruité et fin, aux notes de sous-bois, de petits fruits rouges frais (fraise, framboise) et très floral. Il accompagnera parfaitement une viande blanche (volaille, veau) ou se dégustera simplement en apéritif.', 'Verre 15 cl', 7.9),
  r('Hautes Côtes de Beaune', 'Domaine Germain. Vin fruité et fin, aux notes de sous-bois, de petits fruits rouges frais (fraise, framboise) et très floral. Il accompagnera parfaitement une viande blanche (volaille, veau) ou se dégustera simplement en apéritif.', 'Pichet 50 cl', 30),
  r('Hautes Côtes de Beaune', 'Domaine Germain. Vin fruité et fin, aux notes de sous-bois, de petits fruits rouges frais (fraise, framboise) et très floral. Il accompagnera parfaitement une viande blanche (volaille, veau) ou se dégustera simplement en apéritif.', 'Bouteille 75 cl', 39.5),
  r('Bordeaux Supérieur Château Grand Renom', 'Un vin aromatique et généreux. Belle robe rubis, notes délicates de fruits rouges. Équilibré en bouche, attaque ample et agréable, notes boisées, tanins soyeux et délicats avec une belle fraîcheur aromatique.', 'Bouteille 75 cl', 36),
  // --- Vins Blancs ---
  r('Arbois Chardonnay', 'Domaine Jean Louis Tissot à Montigny-lès-Arsures - AOC.', 'Bouteille 75 cl', 24.9),
  r('Arbois Cuvée Béthanie', 'Fruitière Vinicole d’Arbois - AOC. Très typé jurassien avec ses 60 % de Chardonnay et 40 % de Savagnin.', 'Bouteille 37,5 cl', 19),
  r('Arbois Cuvée Béthanie', 'Fruitière Vinicole d’Arbois - AOC. Très typé jurassien avec ses 60 % de Chardonnay et 40 % de Savagnin.', 'Bouteille 75 cl', 29.9),
  r('Arbois Savagnin', 'Fruitière Vinicole d’Arbois - AOC. Avec des arômes puissants de noix, de vanille et d’amandes grillées, ce grand vin tutoie son illustre parent, le vin jaune. Notre Savagnin s’exprime sur des tonalités complexes typiques du terroir jurassien.', 'Verre 15 cl', 7.2),
  r('Arbois Savagnin', 'Fruitière Vinicole d’Arbois - AOC. Avec des arômes puissants de noix, de vanille et d’amandes grillées, ce grand vin tutoie son illustre parent, le vin jaune. Notre Savagnin s’exprime sur des tonalités complexes typiques du terroir jurassien.', 'Pichet 50 cl', 28),
  r('Arbois Savagnin', 'Fruitière Vinicole d’Arbois - AOC. Avec des arômes puissants de noix, de vanille et d’amandes grillées, ce grand vin tutoie son illustre parent, le vin jaune. Notre Savagnin s’exprime sur des tonalités complexes typiques du terroir jurassien.', 'Bouteille 75 cl', 36),
  r('Saint Véran', 'Domaine du Paradis - AOP. Chardonnay du vignoble Mâconnais.', 'Verre 15 cl', 7.9),
  r('Saint Véran', 'Domaine du Paradis - AOP. Chardonnay du vignoble Mâconnais.', 'Pichet 50 cl', 30),
  r('Saint Véran', 'Domaine du Paradis - AOP. Chardonnay du vignoble Mâconnais.', 'Bouteille 75 cl', 39.5),
  r('Hautes Côtes de Beaune', 'Domaine Germain (blanc). Terroirs en altitude, expression très minérale, vin facile d’accès dans sa jeunesse en apéritif ou en accompagnement. La garde révèle un vin plus gras et volumineux, plus riche et puissant, sur des notes beurrées.', 'Bouteille 75 cl', 39.5),
  r('Chablis St Martin', 'Domaine Laroche - AOC. Grâce à un élevage rigoureux sur lies fines, offre la minéralité caractéristique des meilleurs terroirs de l’appellation.', 'Verre 15 cl', 7.9),
  r('Chablis St Martin', 'Domaine Laroche - AOC. Grâce à un élevage rigoureux sur lies fines, offre la minéralité caractéristique des meilleurs terroirs de l’appellation.', 'Pichet 50 cl', 30),
  r('Chablis St Martin', 'Domaine Laroche - AOC. Grâce à un élevage rigoureux sur lies fines, offre la minéralité caractéristique des meilleurs terroirs de l’appellation.', 'Bouteille 75 cl', 39.5),
  r('Gewurztraminer', 'Château de Riquewihr “Les Sorcières”, Domaine Dopff et Irion - AOC. Vin doux, à l’attaque épicée, milieu de bouche moelleux.', 'Verre 15 cl', 7),
  r('Gewurztraminer', 'Château de Riquewihr “Les Sorcières”, Domaine Dopff et Irion - AOC. Vin doux, à l’attaque épicée, milieu de bouche moelleux.', 'Pichet 50 cl', 27),
  r('Gewurztraminer', 'Château de Riquewihr “Les Sorcières”, Domaine Dopff et Irion - AOC. Vin doux, à l’attaque épicée, milieu de bouche moelleux.', 'Bouteille 75 cl', 35),
  // --- Vins Rosés ---
  r('Clair de Rosé', 'Les Jamelles à Monze, au pied de la Montagne d’Alaric - IGP Pays d’Oc. Assemblage de deux cépages, le Grenache et le Cinsault.', 'Bouteille 75 cl', 18),
  r('Ma Bohème Domaine Pive', 'IGP Camargue. Très rafraîchissante aux notes de fruits frais (ananas, mangue, pêche), longueur, finesse en bouche, finale gourmande subtilement acidulée.', 'Bouteille 75 cl', 29),
  r('Miraval', 'Côtes de Provence - AOP. La cuvée phare de Brad Pitt, vinifiée par la famille Perrin, star de la vallée du Rhône. Élu meilleur rosé du monde par Wine Spectator, le rosé le plus « people » ! Miraval rosé provient des meilleures vignes du château, bénéficiant de sa propre vallée au cœur de la Provence.', 'Bouteille 75 cl', 45),
  // --- Pichets ---
  r('Bourgogne Aligoté', 'Pichet — Blanc. AOC.', 'Verre 15 cl', 3.9),
  r('Bourgogne Aligoté', 'Pichet — Blanc. AOC.', 'Pichet 50 cl', 9.9),
  r('Bourgogne Aligoté', 'Pichet — Blanc. AOC.', 'Pichet 75 cl', 13.9),
  r('Côtes du Rhône', 'Pichet — Rouge. Cave de Chusclan.', 'Verre 15 cl', 3.9),
  r('Côtes du Rhône', 'Pichet — Rouge. Cave de Chusclan.', 'Pichet 50 cl', 9.9),
  r('Côtes du Rhône', 'Pichet — Rouge. Cave de Chusclan.', 'Pichet 75 cl', 13.9),
  r('Côtes de Provence', 'Pichet — Rosé. “Cap des Pins”, Maîtres Vignerons de la Presqu’île de St Tropez - IGP.', 'Verre 15 cl', 3.9),
  r('Côtes de Provence', 'Pichet — Rosé. “Cap des Pins”, Maîtres Vignerons de la Presqu’île de St Tropez - IGP.', 'Pichet 50 cl', 9.9),
  r('Côtes de Provence', 'Pichet — Rosé. “Cap des Pins”, Maîtres Vignerons de la Presqu’île de St Tropez - IGP.', 'Pichet 75 cl', 13.9),
  // --- Pétillants ---
  r('Crémant du Jura Blanc Brut', 'Fruitière Vinicole d’Arbois - AOP. À majorité de Chardonnay, bulles fines, intenses et légères, arômes fruités et floraux typiques de son cépage.', 'Verre 12 cl', 3.9),
  r('Crémant du Jura Blanc Brut', 'Fruitière Vinicole d’Arbois - AOP. À majorité de Chardonnay, bulles fines, intenses et légères, arômes fruités et floraux typiques de son cépage.', 'Bouteille 75 cl', 24),
  r('Crémant du Jura Rosé Brut', 'Fruitière Vinicole d’Arbois - AOP. La robe rose claire provient du Pinot noir, aussi à l’origine du délicat fruité.', 'Bouteille 75 cl', 26),
  r('Cidre Breton “La Bolée d’Armorique” Brut ou Doux', 'AOC.', 'Bouteille 75 cl', 14),
  r('Cidre Normand “Ecusson” Rosé', 'AOC.', 'Bouteille 75 cl', 14),
  r('Cidre La Mordue “Hard Cider”', 'À la fois fruitée, acidulée et pétillante, sans amertume. Fabriquée en France avec des pommes françaises (Coopérative Agrial) ; fermentation courte et dirigée où tout le sucre est transformé en alcool.', 'Bouteille 27,5 cl', 4),
  // --- Boissons chaudes ---
  r('Expresso', '', '', 2.2),
  r('Expresso Crème', '', '', 2.4),
  r('Thé, Infusion', '', '', 3.4),
  r('Double Expresso', '', '', 3.8),
  r('Double Expresso', '', '', 4.2),
  r('Lait Café Viennois', 'Double expresso, chantilly.', '', 5.5),
  r('Café Irlandais', 'Double expresso, 4 cl de whisky, chantilly.', '', 9),
  // --- Digestifs (Verre 4 cl) ---
  r('Liqueur de Bourgeons de Sapin du Haut-Doubs 40°', '', 'Verre 4 cl', 5.2),
  r('Liqueur de Génépi 42°', 'Distillerie les fils d’Émile Pernot à La Cluse et Mijoux.', 'Verre 4 cl', 6.5),
  r('Eau de Vie de Poire Williams 45°', 'Distillerie Peureux à Fougerolles.', 'Verre 4 cl', 6.5),
  r('Eau de Vie de Mirabelle ou Framboise 45°', 'Distillerie Michel à Chapelle des Bois.', 'Verre 4 cl', 6.5),
  r('Vieux Marc de Bourgogne 40°', '', 'Verre 4 cl', 5.2),
  r('Marc du Jura 40°', 'Domaine Tissot.', 'Verre 4 cl', 6.5),
  r('Liqueur de Poire 25°', 'Distillerie Peureux à Fougerolles.', 'Verre 4 cl', 6.5),
  r('Get 27 21°', 'Liqueur de Menthe.', 'Verre 4 cl', 5.2),
  r('Get 31 24°', 'Liqueur de menthe poivrée.', 'Verre 4 cl', 5.2),
  r('Grand Marnier 40°', 'Liqueur à base de Cognac et d’oranges.', 'Verre 4 cl', 5.2),
  r('Cognac 40°', 'Eau-de-vie de vin.', 'Verre 4 cl', 5.2),
  r('Baileys', '', 'Verre 4 cl', 5.2),
]

// ============================================================================
const fichiers = [
  { nom: 'carte_vins-boissons_08:02:21.xls', rows: carte_08 },
  { nom: 'carte_vins-boissons_20:07:21.xls', rows: carte_20 },
  { nom: 'carte_vins-boissons_26:04:23_aujourdhui.xls', rows: carte_26 },
]

for (const f of fichiers) {
  const aoa = [HEADER, ...f.rows]
  const ws = XLSX.utils.aoa_to_sheet(aoa)
  ws['!cols'] = [{ wch: 40 }, { wch: 75 }, { wch: 22 }, { wch: 10 }]
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Vins & boissons')
  XLSX.writeFile(wb, path.join(dir, f.nom), { bookType: 'biff8' })
  console.log(`OK  ${f.nom}  (${f.rows.length} lignes)`)
}
