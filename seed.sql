-- Seed data: ~10 popular board games (Danish fun facts & awards)
-- Idempotent: safe to re-run via `make seed` (truncates scans, upserts games)

TRUNCATE scans RESTART IDENTITY CASCADE;

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
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    year_published = EXCLUDED.year_published,
    awards = EXCLUDED.awards,
    fun_fact = EXCLUDED.fun_fact,
    wikipedia_url = EXCLUDED.wikipedia_url;
