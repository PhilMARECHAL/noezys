/* ═══════════════════════════════════════════════════════════
   NOEZYS — Menu Translator (FR → NL)
   Professional, certification-grade culinary translation engine.
   100% client-side · curated gastronomic lexicon · longest-match.
   ═══════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ── 1. CURATED CULINARY LEXICON (Français → Nederlands) ─────
     Keys MUST be lowercase, using straight apostrophes.
     Multi-word entries are matched first (longest-match wins),
     so "pomme de terre" beats "pomme", "magret de canard" beats
     "canard", etc. This is what gives the output its
     professional, menu-aware quality.
     ─────────────────────────────────────────────────────────── */
  const LEXICON = {
    /* ── Menu sections & structure ── */
    'menu': 'menu',
    'carte': 'menukaart',
    'la carte': 'de menukaart',
    'formule': 'formule',
    'formule du jour': 'dagmenu',
    'menu du jour': 'dagmenu',
    'menu enfant': 'kindermenu',
    'menu dégustation': 'degustatiemenu',
    'entrée': 'voorgerecht',
    'entrées': 'voorgerechten',
    'amuse-bouche': 'amuse',
    'amuse-bouches': 'amuses',
    'mise en bouche': 'amuse',
    'plat': 'hoofdgerecht',
    'plats': 'hoofdgerechten',
    'plat principal': 'hoofdgerecht',
    'plats principaux': 'hoofdgerechten',
    'plat du jour': 'dagschotel',
    'suggestion': 'suggestie',
    'suggestions': 'suggesties',
    'suggestion du chef': 'suggestie van de chef',
    'spécialité': 'specialiteit',
    'spécialités': 'specialiteiten',
    'spécialité de la maison': 'specialiteit van het huis',
    'accompagnement': 'bijgerecht',
    'accompagnements': 'bijgerechten',
    'garniture': 'garnituur',
    'dessert': 'nagerecht',
    'desserts': 'nagerechten',
    'fromage': 'kaas',
    'fromages': 'kazen',
    'plateau de fromages': 'kaasplank',
    'boisson': 'drank',
    'boissons': 'dranken',
    'apéritif': 'aperitief',
    'apéritifs': 'aperitieven',
    'digestif': 'digestief',
    'entremets': 'tussengerecht',
    'à partager': 'om te delen',
    'à emporter': 'om mee te nemen',
    'sur place': 'ter plaatse',
    'du jour': 'van de dag',
    'maison': 'van het huis',
    'fait maison': 'huisgemaakt',
    'de saison': 'van het seizoen',
    'au choix': 'naar keuze',
    'selon arrivage': 'afhankelijk van de aanvoer',
    'assortiment': 'assortiment',
    'sélection': 'selectie',
    'dégustation': 'degustatie',

    /* ── Soups, salads, starters ── */
    'soupe': 'soep',
    'potage': 'soep',
    'velouté': 'roomsoep',
    'bouillon': 'bouillon',
    'consommé': 'consommé',
    'bisque': 'bisque',
    'salade': 'salade',
    'salade verte': 'groene salade',
    'salade composée': 'gemengde salade',
    'crudités': 'rauwkost',
    'terrine': 'terrine',
    'pâté': 'paté',
    'rillettes': 'rillettes',
    'tartare': 'tartaar',
    'carpaccio': 'carpaccio',
    'tartine': 'boterham',
    'œuf': 'ei',
    'œufs': 'eieren',
    'oeuf': 'ei',
    'oeufs': 'eieren',
    'omelette': 'omelet',
    'quiche': 'quiche',
    'gratin': 'gratin',

    /* ── Cooking methods & textures ── */
    'grillé': 'gegrild',
    'grillée': 'gegrild',
    'grillés': 'gegrild',
    'grillées': 'gegrild',
    'rôti': 'gebraden',
    'rôtie': 'gebraden',
    'rôtis': 'gebraden',
    'frit': 'gefrituurd',
    'frite': 'gefrituurd',
    'frits': 'gefrituurd',
    'poêlé': 'gebakken in de pan',
    'poêlée': 'gebakken in de pan',
    'braisé': 'gesmoord',
    'braisée': 'gesmoord',
    'mijoté': 'gestoofd',
    'mijotée': 'gestoofd',
    'fumé': 'gerookt',
    'fumée': 'gerookt',
    'mariné': 'gemarineerd',
    'marinée': 'gemarineerd',
    'confit': 'gekonfijt',
    'confite': 'gekonfijt',
    'pané': 'gepaneerd',
    'panée': 'gepaneerd',
    'gratiné': 'gegratineerd',
    'gratinée': 'gegratineerd',
    'flambé': 'geflambeerd',
    'flambée': 'geflambeerd',
    'fondant': 'smeuïg',
    'croustillant': 'krokant',
    'croustillante': 'krokant',
    'cru': 'rauw',
    'crue': 'rauw',
    'mi-cuit': 'half gegaard',
    'saignant': 'rood gebakken',
    'à point': 'medium gebakken',
    'bien cuit': 'doorbakken',
    'vapeur': 'gestoomd',
    'à la vapeur': 'gestoomd',
    'au four': 'uit de oven',
    'à la plancha': 'van de plancha',
    'au feu de bois': 'op houtvuur',
    'à la broche': 'aan het spit',
    'écrasé': 'gestampt',
    'écrasée': 'gestampt',
    'caramélisé': 'gekarameliseerd',
    'caramélisée': 'gekarameliseerd',
    'snacké': 'kort aangebakken',
    'rosé': 'rosé gebakken',

    /* ── Meat & poultry ── */
    'viande': 'vlees',
    'viandes': 'vlees',
    'bœuf': 'rundvlees',
    'boeuf': 'rundvlees',
    'veau': 'kalfsvlees',
    'agneau': 'lamsvlees',
    'porc': 'varkensvlees',
    'poulet': 'kip',
    'volaille': 'gevogelte',
    'canard': 'eend',
    'magret de canard': 'eendenborst',
    'cuisse de canard': 'eendenbout',
    'dinde': 'kalkoen',
    'pintade': 'parelhoen',
    'caille': 'kwartel',
    'pigeon': 'duif',
    'lapin': 'konijn',
    'gibier': 'wild',
    'chevreuil': 'ree',
    'sanglier': 'everzwijn',
    'jambon': 'ham',
    'jambon cru': 'rauwe ham',
    'lard': 'spek',
    'lardons': 'spekblokjes',
    'saucisse': 'worst',
    'saucisson': 'droge worst',
    'merguez': 'merguez',
    'boudin': 'bloedworst',
    'andouillette': 'pensworst',
    'côte': 'rib',
    'côte de bœuf': 'rib van rund',
    'côtelette': 'kotelet',
    'entrecôte': 'entrecote',
    'filet de bœuf': 'runderfilet',
    'filet de boeuf': 'runderfilet',
    'filet': 'filet',
    'filet mignon': 'varkenshaas',
    'faux-filet': 'contrefilet',
    'bavette': 'bavette',
    'onglet': 'longhaas',
    'gigot': 'lamsbout',
    'gigot d\'agneau': 'lamsbout',
    'souris d\'agneau': 'lamsschenkel',
    'carré d\'agneau': 'lamsrack',
    'foie gras': 'foie gras',
    'foie': 'lever',
    'ris de veau': 'kalfszwezerik',
    'rognons': 'niertjes',
    'joue de bœuf': 'runderwang',
    'pot-au-feu': 'hutspot',
    'blanquette': 'blanquette',
    'bourguignon': 'bourguignon',
    'brochette': 'spies',
    'brochettes': 'spiesjes',

    /* ── Fish & seafood ── */
    'poisson': 'vis',
    'poissons': 'vis',
    'saumon': 'zalm',
    'saumon fumé': 'gerookte zalm',
    'thon': 'tonijn',
    'cabillaud': 'kabeljauw',
    'morue': 'stokvis',
    'bar': 'zeebaars',
    'loup de mer': 'zeebaars',
    'dorade': 'dorade',
    'truite': 'forel',
    'sole': 'tong',
    'turbot': 'tarbot',
    'lotte': 'zeeduivel',
    'lieu': 'koolvis',
    'hareng': 'haring',
    'maquereau': 'makreel',
    'sardine': 'sardine',
    'sardines': 'sardines',
    'anchois': 'ansjovis',
    'rouget': 'zeebarbeel',
    'raie': 'rog',
    'fruits de mer': 'zeevruchten',
    'crevette': 'garnaal',
    'crevettes': 'garnalen',
    'gambas': 'gamba\'s',
    'moule': 'mossel',
    'moules': 'mosselen',
    'moules-frites': 'mosselen met frieten',
    'huître': 'oester',
    'huîtres': 'oesters',
    'homard': 'kreeft',
    'langouste': 'langoest',
    'langoustine': 'langoustine',
    'langoustines': 'langoustines',
    'écrevisse': 'rivierkreeft',
    'crabe': 'krab',
    'tourteau': 'noordzeekrab',
    'coquille saint-jacques': 'sint-jakobsschelp',
    'coquilles saint-jacques': 'sint-jakobsschelpen',
    'noix de saint-jacques': 'coquilles',
    'saint-jacques': 'coquilles',
    'calamar': 'inktvis',
    'calamars': 'inktvis',
    'encornet': 'pijlinktvis',
    'poulpe': 'octopus',
    'seiche': 'zeekat',
    'bulot': 'wulk',

    /* ── Vegetables, starch & grains ── */
    'légume': 'groente',
    'légumes': 'groenten',
    'pomme de terre': 'aardappel',
    'pommes de terre': 'aardappelen',
    'pommes': 'aardappelen',
    'frites': 'frieten',
    'purée': 'puree',
    'gratin dauphinois': 'aardappelgratin',
    'carotte': 'wortel',
    'carottes': 'wortelen',
    'haricot vert': 'sperzieboon',
    'haricots verts': 'sperziebonen',
    'petits pois': 'doperwten',
    'épinard': 'spinazie',
    'épinards': 'spinazie',
    'chou': 'kool',
    'chou-fleur': 'bloemkool',
    'chou rouge': 'rode kool',
    'choucroute': 'zuurkool',
    'brocoli': 'broccoli',
    'champignon': 'champignon',
    'champignons': 'champignons',
    'cèpe': 'eekhoorntjesbrood',
    'cèpes': 'eekhoorntjesbrood',
    'girolle': 'cantharel',
    'girolles': 'cantharellen',
    'truffe': 'truffel',
    'oignon': 'ui',
    'oignons': 'uien',
    'ail': 'knoflook',
    'échalote': 'sjalot',
    'tomate': 'tomaat',
    'tomates': 'tomaten',
    'courgette': 'courgette',
    'aubergine': 'aubergine',
    'poivron': 'paprika',
    'poireau': 'prei',
    'poireaux': 'prei',
    'asperge': 'asperge',
    'asperges': 'asperges',
    'endive': 'witlof',
    'betterave': 'biet',
    'potiron': 'pompoen',
    'courge': 'pompoen',
    'lentilles': 'linzen',
    'haricots blancs': 'witte bonen',
    'riz': 'rijst',
    'risotto': 'risotto',
    'pâtes': 'pasta',
    'nouilles': 'noedels',
    'tagliatelles': 'tagliatelle',
    'gnocchi': 'gnocchi',
    'polenta': 'polenta',
    'semoule': 'griesmeel',
    'couscous': 'couscous',
    'pain': 'brood',

    /* ── Fruit ── */
    'fruit': 'fruit',
    'fruits': 'fruit',
    'fruits rouges': 'rode vruchten',
    'pomme': 'appel',
    'poire': 'peer',
    'fraise': 'aardbei',
    'fraises': 'aardbeien',
    'framboise': 'framboos',
    'framboises': 'frambozen',
    'myrtille': 'bosbes',
    'myrtilles': 'bosbessen',
    'cerise': 'kers',
    'cerises': 'kersen',
    'pêche': 'perzik',
    'abricot': 'abrikoos',
    'citron': 'citroen',
    'citron vert': 'limoen',
    'orange': 'sinaasappel',
    'pamplemousse': 'pompelmoes',
    'ananas': 'ananas',
    'mangue': 'mango',
    'fruit de la passion': 'passievrucht',
    'raisin': 'druif',
    'figue': 'vijg',
    'figues': 'vijgen',
    'prune': 'pruim',
    'rhubarbe': 'rabarber',
    'marron': 'kastanje',
    'marrons': 'kastanjes',

    /* ── Dairy & basics ── */
    'beurre': 'boter',
    'crème': 'room',
    'crème fraîche': 'crème fraîche',
    'lait': 'melk',
    'yaourt': 'yoghurt',
    'chèvre': 'geitenkaas',
    'mozzarella': 'mozzarella',
    'parmesan': 'parmezaan',
    'comté': 'comté',
    'roquefort': 'roquefort',
    'brie': 'brie',
    'burrata': 'burrata',

    /* ── Desserts & sweets ── */
    'gâteau': 'taart',
    'tarte': 'taart',
    'tarte aux pommes': 'appeltaart',
    'tarte tatin': 'tarte tatin',
    'tarte au citron': 'citroentaart',
    'glace': 'ijs',
    'glace vanille': 'vanille-ijs',
    'sorbet': 'sorbet',
    'crêpe': 'pannenkoek',
    'crêpes': 'pannenkoeken',
    'gaufre': 'wafel',
    'mousse': 'mousse',
    'mousse au chocolat': 'chocolademousse',
    'crème brûlée': 'crème brûlée',
    'île flottante': 'drijvend eiland',
    'profiterole': 'soes',
    'profiteroles': 'soesjes',
    'éclair': 'éclair',
    'macaron': 'makaron',
    'macarons': 'makarons',
    'tiramisu': 'tiramisu',
    'panna cotta': 'panna cotta',
    'fondant au chocolat': 'chocoladetaartje',
    'moelleux au chocolat': 'chocoladetaartje',
    'mille-feuille': 'tompoes',
    'clafoutis': 'clafoutis',
    'compote': 'compote',
    'salade de fruits': 'fruitsalade',
    'chocolat': 'chocolade',
    'chocolat noir': 'pure chocolade',
    'vanille': 'vanille',
    'caramel': 'karamel',
    'caramel au beurre salé': 'gezouten karamel',
    'miel': 'honing',
    'noix': 'walnoot',
    'noix de coco': 'kokosnoot',
    'amande': 'amandel',
    'amandes': 'amandelen',
    'noisette': 'hazelnoot',
    'noisettes': 'hazelnoten',
    'pistache': 'pistache',
    'sucre': 'suiker',
    'confiture': 'confituur',
    'pâtisserie': 'gebak',
    'pâtisseries': 'gebak',
    'viennoiserie': 'zoet broodje',

    /* ── Sauces, condiments, seasoning ── */
    'sauce': 'saus',
    'jus': 'jus',
    'jus de viande': 'vleesjus',
    'vinaigrette': 'vinaigrette',
    'mayonnaise': 'mayonaise',
    'aïoli': 'aïoli',
    'sauce béarnaise': 'bearnaisesaus',
    'sauce hollandaise': 'hollandaisesaus',
    'beurre blanc': 'beurre blanc',
    'béarnaise': 'bearnaisesaus',
    'hollandaise': 'hollandaisesaus',
    'pesto': 'pesto',
    'coulis': 'coulis',
    'réduction': 'reductie',
    'émulsion': 'emulsie',
    'huile': 'olie',
    'huile d\'olive': 'olijfolie',
    'vinaigre': 'azijn',
    'vinaigre balsamique': 'balsamicoazijn',
    'sel': 'zout',
    'fleur de sel': 'fleur de sel',
    'poivre': 'peper',
    'moutarde': 'mosterd',
    'cornichon': 'augurk',
    'cornichons': 'augurken',
    'câpres': 'kappertjes',
    'herbes': 'kruiden',
    'fines herbes': 'verse kruiden',
    'persil': 'peterselie',
    'basilic': 'basilicum',
    'thym': 'tijm',
    'romarin': 'rozemarijn',
    'estragon': 'dragon',
    'ciboulette': 'bieslook',
    'aneth': 'dille',
    'coriandre': 'koriander',
    'menthe': 'munt',
    'safran': 'saffraan',
    'curry': 'kerrie',
    'paprika': 'paprikapoeder',
    'épices': 'specerijen',
    'gingembre': 'gember',
    'piment': 'chilipeper',

    /* ── Drinks ── */
    'vin': 'wijn',
    'vins': 'wijnen',
    'vin rouge': 'rode wijn',
    'vin blanc': 'witte wijn',
    'vin rosé': 'rosé',
    'verre de vin': 'glas wijn',
    'bouteille': 'fles',
    'pichet': 'karaf',
    'champagne': 'champagne',
    'bière': 'bier',
    'bière pression': 'bier van het vat',
    'cidre': 'cider',
    'eau': 'water',
    'eau plate': 'plat water',
    'eau gazeuse': 'bruisend water',
    'eau minérale': 'mineraalwater',
    'jus de fruits': 'vruchtensap',
    'jus d\'orange': 'sinaasappelsap',
    'café': 'koffie',
    'café crème': 'koffie verkeerd',
    'expresso': 'espresso',
    'thé': 'thee',
    'infusion': 'kruidenthee',
    'chocolat chaud': 'warme chocolademelk',
    'limonade': 'limonade',

    /* ── Connectors & qualifiers ── */
    'et': 'en',
    'ou': 'of',
    'avec': 'met',
    'sans': 'zonder',
    'sur': 'op',
    'sous': 'onder',
    'dans': 'in',
    'de': 'van',
    'des': 'van de',
    'du': 'van de',
    'au': 'met',
    'aux': 'met',
    'à la': 'met',
    'à l\'': 'met ',
    'd\'': 'van ',
    'le': 'de',
    'la': 'de',
    'les': 'de',
    'son': 'zijn',
    'sa': 'zijn',
    'ses': 'zijn',
    'accompagné de': 'geserveerd met',
    'accompagnée de': 'geserveerd met',
    'servi avec': 'geserveerd met',
    'servie avec': 'geserveerd met',
    'servi': 'geserveerd',
    'garni de': 'gegarneerd met',
    'nappé de': 'overgoten met',
    'parfumé': 'op smaak gebracht',
    'relevé': 'pittig gekruid',
    'petit': 'klein',
    'petite': 'klein',
    'grand': 'groot',
    'grande': 'groot',
    'frais': 'vers',
    'fraîche': 'vers',
    'fraîches': 'vers',
    'chaud': 'warm',
    'chaude': 'warm',
    'froid': 'koud',
    'froide': 'koud',
    'tiède': 'lauwwarm',
    'nouveau': 'nieuw',
    'traditionnel': 'traditioneel',
    'traditionnelle': 'traditioneel',
    'classique': 'klassiek',
    'bio': 'biologisch',
    'végétarien': 'vegetarisch',
    'végétarienne': 'vegetarisch',
    'végétalien': 'veganistisch',
    'épicé': 'pittig',
    'épicée': 'pittig',
    'doux': 'zacht',
    'crémeux': 'romig',
    'crémeuse': 'romig',
    'maison)': 'van het huis)',
  };

  /* Pre-sort keys longest-first so multi-word phrases win. */
  const SORTED_KEYS = Object.keys(LEXICON).sort((a, b) => b.length - a.length);

  /* A character is part of a word if it's a letter, apostrophe or hyphen. */
  const WORD_CHAR = /[\p{L}'’\-]/u;
  function isWordChar(ch) {
    return !!ch && WORD_CHAR.test(ch);
  }

  function applyCase(src, dst) {
    // ALL CAPS source → ALL CAPS target (section headers like "ENTRÉES")
    if (src === src.toUpperCase() && src !== src.toLowerCase()) {
      return dst.toUpperCase();
    }
    // Capitalised first letter → capitalise target
    if (src[0] === src[0].toUpperCase() && src[0] !== src[0].toLowerCase()) {
      return dst.charAt(0).toUpperCase() + dst.slice(1);
    }
    return dst;
  }

  /* Core engine: walk the text, longest-match at every word boundary. */
  function translate(text) {
    const lower = text.toLowerCase().replace(/’/g, '\'');
    let out = '';
    let i = 0;
    let recognizedWords = 0;
    let totalWords = (text.match(/\p{L}[\p{L}'’\-]*/gu) || []).length;

    while (i < text.length) {
      const ch = text[i];
      const atBoundary = isWordChar(ch) && (i === 0 || !isWordChar(text[i - 1]));

      if (atBoundary) {
        let matchedKey = null;
        for (const key of SORTED_KEYS) {
          if (lower.startsWith(key, i)) {
            const after = text[i + key.length];
            // Keys ending in apostrophe (d') legitimately precede a letter.
            const keyEndsApostrophe = key.charAt(key.length - 1) === '\'';
            if (keyEndsApostrophe || !isWordChar(after)) {
              matchedKey = key;
              break;
            }
          }
        }

        if (matchedKey) {
          const matched = text.substr(i, matchedKey.length);
          out += applyCase(matched, LEXICON[matchedKey]);
          recognizedWords += matchedKey.split(/[\s'’\-]+/).filter(Boolean).length;
          i += matchedKey.length;
          continue;
        }
      }

      out += ch;
      i++;
    }

    const confidence = totalWords === 0
      ? 0
      : Math.min(100, Math.round((recognizedWords / totalWords) * 100));

    return { text: out, confidence, totalWords, recognizedWords };
  }

  /* ── 2. SAMPLE MENU ────────────────────────────────────────── */
  const SAMPLE = `Menu du jour

ENTRÉES
Velouté de potiron et huile de noisette — 9 €
Foie gras maison, chutney de figues — 16 €
Salade de chèvre chaud et lardons — 12 €

PLATS
Magret de canard, sauce au miel et pommes de terre grillées — 24 €
Filet de bœuf, sauce béarnaise et frites maison — 28 €
Cabillaud rôti, légumes de saison et beurre blanc — 22 €
Risotto aux champignons et truffe — 19 €

DESSERTS
Crème brûlée à la vanille — 8 €
Fondant au chocolat, glace vanille — 9 €
Tarte tatin et crème fraîche — 8 €

BOISSONS
Verre de vin rouge — 6 €
Café — 3 €`;

  /* ── 3. UI WIRING ──────────────────────────────────────────── */
  const $ = (id) => document.getElementById(id);

  const input = $('mt-input');
  const output = $('mt-output');
  const certBlock = $('mt-cert');
  const certDate = $('mt-cert-date');
  const certRef = $('mt-cert-ref');
  const confFill = $('mt-conf-fill');
  const confLabel = $('mt-conf-label');
  const resultPanel = $('mt-result');

  function pad(n) { return String(n).padStart(2, '0'); }

  function makeRef() {
    const d = new Date();
    const stamp = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}`;
    const rand = Math.random().toString(36).slice(2, 7).toUpperCase();
    return `NZ-${stamp}-${rand}`;
  }

  function run() {
    const src = input.value.trim();
    if (!src) {
      input.focus();
      input.classList.add('mt-shake');
      setTimeout(() => input.classList.remove('mt-shake'), 500);
      return;
    }

    const res = translate(src);

    // Render the translation, preserving line structure.
    output.textContent = res.text;

    // Confidence meter.
    confFill.style.width = res.confidence + '%';
    confLabel.textContent = `${res.confidence}% — ${res.recognizedWords}/${res.totalWords} termes reconnus`;
    confFill.classList.toggle('mt-conf--high', res.confidence >= 80);
    confFill.classList.toggle('mt-conf--mid', res.confidence >= 55 && res.confidence < 80);
    confFill.classList.toggle('mt-conf--low', res.confidence < 55);

    // Certification stamp.
    const now = new Date();
    certDate.textContent = now.toLocaleDateString('fr-BE', {
      day: '2-digit', month: 'long', year: 'numeric',
    });
    certRef.textContent = makeRef();

    resultPanel.hidden = false;
    resultPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  $('mt-translate').addEventListener('click', run);

  $('mt-sample').addEventListener('click', () => {
    input.value = SAMPLE;
    input.focus();
  });

  $('mt-clear').addEventListener('click', () => {
    input.value = '';
    resultPanel.hidden = true;
    input.focus();
  });

  // Ctrl/Cmd + Enter to translate.
  input.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      run();
    }
  });

  $('mt-copy').addEventListener('click', async () => {
    const btn = $('mt-copy');
    try {
      await navigator.clipboard.writeText(output.textContent);
      const orig = btn.textContent;
      btn.textContent = 'Copié ✓';
      setTimeout(() => { btn.textContent = orig; }, 1600);
    } catch {
      // Fallback selection
      const range = document.createRange();
      range.selectNodeContents(output);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    }
  });

  $('mt-print').addEventListener('click', () => {
    window.print();
  });

})();
