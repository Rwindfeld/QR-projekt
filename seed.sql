-- Seed / upsert board games (Danish fun facts). Does NOT delete scans.
-- To wipe scans for testing: run seed-reset.sql

INSERT INTO games (slug, name, year_published, awards, fun_fact, wikipedia_url) VALUES
(
    'ticket-to-ride',
    'Ticket to Ride',
    2004,
    'Spiel des Jahres 2004 (Tyskland)',
    'Spillet startede som et jernbane-spil på en ridder-tema prototype — designer Alan R. Moon skiftede til tog, og resten er historie.',
    'https://da.wikipedia.org/wiki/Ticket_to_Ride_(spil)'
),
(
    'catan',
    'Catan',
    1995,
    'Spiel des Jahres 1995; verdens mest solgte strategispil i mange år',
    'På Bornholm findes en officiel Catan-udgave med lokale ressourcer — perfekt café-snak mens I bygger veje.',
    'https://da.wikipedia.org/wiki/Settlers'
),
(
    'carcassonne',
    'Carcassonne',
    2000,
    'Spiel des Jahres 2001; Deutscher Spiele Preis 2000',
    'Byen Carcassonne i Frankrig har rigtig middelaldermur — mange spillere genkender landskabet fra feriebilleder.',
    'https://en.wikipedia.org/wiki/Carcassonne_(board_game)'
),
(
    'azul',
    'Azul',
    2017,
    'Spiel des Jahres Kennerspiel 2018',
    'Fliserne er inspireret af portugisiske azulejos; designer Michael Kiesling ville fange lysrefleksion i keramik.',
    'https://en.wikipedia.org/wiki/Azul_(board_game)'
),
(
    'wingspan',
    'Wingspan',
    2019,
    'Kennerspiel des Jahres 2020',
    'Hvert kort har en rigtig fugleart med fakta — mange café-spillere opdager en ny favoritfugl efter første runde.',
    'https://en.wikipedia.org/wiki/Wingspan_(board_game)'
),
(
    '7-wonders',
    '7 Wonders',
    2010,
    'Kennerspiel des Jahres 2011; Origins Award 2011',
    'Alle spiller samtidig i tre aldre — derfor føles runden hurtig selv med syv spillere ved ét langt cafébord.',
    'https://en.wikipedia.org/wiki/7_Wonders_(board_game)'
),
(
    'splendor',
    'Splendor',
    2014,
    'Golden Geek Best Family Game 2014',
    'Chipsene er tungere end de ser ud — mange grupper laver uofficielle regler om at “klirre” ved køb af ædelsten.',
    'https://en.wikipedia.org/wiki/Splendor_(board_game)'
),
(
    'codenames',
    'Codenames',
    2015,
    'Spiel des Jahres 2016',
    'Dansk version findes med danske ord — perfekt til blandede gæstegrupper i et spilcafé.',
    'https://en.wikipedia.org/wiki/Codenames_(board_game)'
),
(
    'pandemic',
    'Pandemic',
    2008,
    'Z-Man Games; ofte nævnt som gateway kooperativt spil',
    'Kooperativt design betyder at I vinder eller taber sammen — mindre “take that” ved nabobordet.',
    'https://en.wikipedia.org/wiki/Pandemic_(board_game)'
),
(
    'dixit',
    'Dixit',
    2008,
    'Spiel des Jahres 2010',
    'Illustrationerne er bevidst åbne — samme billede kan betyde helt forskellige ting afhængigt af hvem der fortæller.',
    'https://en.wikipedia.org/wiki/Dixit_(board_game)'
),
(
    'king-of-tokyo',
    'King of Tokyo',
    2011,
    'Gouden Ludo 2012; populær “monster-kamp”-klassiker',
    'Terninger og kaiju-humor gør det nemt at forklare reglerne på under to minutter ved et cafébord.',
    'https://en.wikipedia.org/wiki/King_of_Tokyo'
),
(
    'terraforming-mars',
    'Terraforming Mars',
    2016,
    'Kennerspiel des Jahres 2017; Golden Geek 2017',
    'Korporationsnavnene i spillet er inside-jokes — nørder elsker at spotte referencer mellem runderne.',
    'https://en.wikipedia.org/wiki/Terraforming_Mars_(board_game)'
),
(
    'kingdomino',
    'Kingdomino',
    2016,
    'Spiel des Jahres 2017',
    'Domino-princip kombineret med slot-valg — hurtigt at lære, men svært at vinde konsekvent.',
    'https://en.wikipedia.org/wiki/Kingdomino'
),
(
    'sushi-go',
    'Sushi Go!',
    2013,
    'Golden Geek Best Card Game 2013',
    'Kortene deles i runde “retter” — mange grupper spiller med lyden “sushi-go” når en runde slutter.',
    'https://en.wikipedia.org/wiki/Sushi_Go!'
),
(
    'patchwork',
    'Patchwork',
    2014,
    'Spiel des Jahres nomineret; 2-spillers klassiker',
    'To spillere bygger et tæppe af felter — perfekt til et lille cafébord mens I venter på maden.',
    'https://en.wikipedia.org/wiki/Patchwork_(board_game)'
),
(
    'root',
    'Root',
    2018,
    'Golden Geek Best Wargame 2018',
    'Skovdyr med asymmetriske roller — reglerne tager tid, men café-grupper der elsker strategi bliver fanget.',
    'https://en.wikipedia.org/wiki/Root_(board_game)'
),
(
    'everdell',
    'Everdell',
    2018,
    'Golden Geek Best Board Game 2018',
    'Det store træ på bordet får ofte komplimenter før første runde — “wow-faktor” ved hylden.',
    'https://en.wikipedia.org/wiki/Everdell'
),
(
    'cascadia',
    'Cascadia',
    2021,
    'Spiel des Jahres 2022; Kennerspiel 2022',
    'Vinder kombination af habitat-heks og dyrekort — ofte kaldt “det smukke spil” i spilcaféer.',
    'https://en.wikipedia.org/wiki/Cascadia_(board_game)'
),
(
    'exploding-kittens',
    'Exploding Kittens',
    2015,
    'Kickstarter-rekord; party-spil',
    'Startede som en af de mest succesfulde Kickstarter-kampagner nogensinde — nemt at tage frem til en hurtig runde.',
    'https://en.wikipedia.org/wiki/Exploding_Kittens'
),
(
    'the-quacks-of-quedlinburg',
    'The Quacks of Quedlinburg',
    2018,
    'Kennerspiel des Jahres 2018',
    'I trækker ingredienser fra en pose — “push your luck” uden at det føles som gambling for nye spillere.',
    'https://en.wikipedia.org/wiki/The_Quacks_of_Quedlinburg'
),
(
    'love-letter',
    'Love Letter',
    2012,
    'Golden Geek Best Card Game 2012',
    'Kun 16 kort i bunken — kan spilles overalt, også når caféen er støjende og bordet er småt.',
    'https://en.wikipedia.org/wiki/Love_Letter_(card_game)'
),
(
    'scythe',
    'Scythe',
    2016,
    'Kennerspiel des Jahres 2017; As d''Or 2017',
    'Alternativ 1920’er-Europa med mechs og bønder — ofte reserveret til “spilaften”-bordet bagerst i caféen.',
    'https://en.wikipedia.org/wiki/Scythe_(board_game)'
),
(
    'klask',
    'Klask',
    2014,
    'Dansk design; Brycecorden Games',
    'Dansk party-klassiker med magnet og disc — larmer lidt, så det er perfekt til livlige spilcafé-aftener.',
    'https://da.wikipedia.org/wiki/Klask'
),
(
    'risk',
    'Risk',
    1957,
    'Klassisk verdenserobring; mange husker det fra ungdommen',
    'Et af de ældste mainstream-brætspil — dansk Wikipedia har en artikel under navnet Risk.',
    'https://da.wikipedia.org/wiki/Risk'
),
(
    'monopoly',
    'Matador',
    1936,
    'Dansk klassiker (Monopoly); C. Drechsler / Brio',
    'I Danmark kender de fleste det som Matador — samme idé som Monopoly, men med danske gadenavne.',
    'https://da.wikipedia.org/wiki/Matador_(br%C3%A6tspil)'
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    year_published = EXCLUDED.year_published,
    awards = EXCLUDED.awards,
    fun_fact = EXCLUDED.fun_fact,
    wikipedia_url = EXCLUDED.wikipedia_url;
