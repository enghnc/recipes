"""Equipment capacity model.

Ingredient quantities scale linearly. Equipment does not. This table records what
actually constrains each menu, so the app can answer "does it still fit on two
kettles, and what vessel do I need?" rather than silently doubling a number.

Vessel types
  dutch   {qt8}                      liquid/bulk volume needed at 8 servings
  skillet {loads8}                   12-inch cast-iron pan loads at 8 servings
  grate   {sqin8, zone}              cooking-grate footprint; zone direct|indirect|full
  spit    {lb8, len8}                rotisserie load weight and inches of spit used
  stone   {units8, minEach}          items cooked one-ish at a time on the pizza stone
  vortex  {pieces8}                  items ringed around a vortex
  steamer {qt8}                      the big steaming pan/pot
  fry     {qt8}                      pot of frying oil (oil never scales; batches do)
  pan     {name, count8, perUnit}    foil pans, muffin tins, loaf pans
"""

KETTLE = {
    "grateDirect": 210,      # sq in of usable hot zone on a 22" kettle
    "grateIndirect": 250,    # sq in in the shadow of a deflector / banked fire
    "grateFull": 350,        # sq in wall to wall
    "spitLb": 15,            # practical load for a domestic rotisserie motor
    "spitLen": 17,           # usable inches between the forks
    "stoneIn": 15,           # a standard round stone
    "vortexPieces": 30,      # wings that fit in a ring without touching
    "steamerQt": 20,         # biggest pan that sits on the grate with the lid down
    "dutchSizes": [4, 6, 9, 12],
    "kettles": 2,
}

CAPACITY = {
# ---------------------------------------------------------------- Part Four
"ch25": dict(maxServes=16, fuel=4, items=[
  dict(match="Tira de Asado", type="grate", sqin8=200, zone="direct",
       note="Flanken ribs need a single uncrowded layer over the embers."),
  dict(match="Entra", type="grate", sqin8=110, zone="direct"),
  dict(match="Choripán", type="grate", sqin8=100, zone="direct"),
  dict(match="Provoleta", type="skillet", loads8=1,
       note="Two discs fill a 12-inch pan. More discs means more pans or more rounds."),
], notes=["Kettle A is ember-only and can be rebuilt between rounds, so this menu scales further than most — you are trading time, not capacity."]),

"ch26": dict(maxServes=12, fuel=4.5, items=[
  dict(match="Brisket", type="grate", sqin8=185, zone="indirect",
       note="A second packer will not fit beside the first. Above 8, buy ONE bigger brisket (16–18 lb) rather than two — same grate, longer cook."),
  dict(match="Ribs", type="grate", sqin8=170, zone="indirect",
       note="Above 4 racks you need a vertical rib rack; laid flat they will not fit."),
  dict(match="Vortex Wings", type="vortex", pieces8=32),
  dict(match="Baked Beans", type="skillet", loads8=1),
  dict(match="Cobbler", type="dutch", qt8=5,
       note="Fruit plus topping. This is the vessel that breaks first when you double the menu."),
], notes=["At 16 the brisket and ribs cannot share two kettles with the wings and cobbler. Bake the cobbler the day before in the same Dutch oven, and skip the vortex round."]),

"ch27": dict(maxServes=16, fuel=3, items=[
  dict(match="Negima", type="grate", sqin8=170, zone="direct",
       note="A robata channel takes about 10 skewers at a time — count rounds, not area."),
  dict(match="Tsukune", type="grate", sqin8=110, zone="direct"),
  dict(match="Miso-Glazed Saba", type="grate", sqin8=120, zone="direct"),
  dict(match="Vegetable Skewers", type="dutch", qt8=3.5,
       note="The rice pot, not the skewers — 3 cups raw rice wants a 4-qt minimum."),
], notes=["Skewers are the most scalable format in this book. Everything is small, fast and cooked in rounds, so 16 costs you about 25 extra minutes of standing at the fire."]),

"ch28": dict(maxServes=12, fuel=3, items=[
  dict(match="Whole Grilled Branzino", type="grate", sqin8=250, zone="direct",
       note="Six 1 lb fish in baskets already fill a 22-inch grate. Beyond that, cook in rounds and serve the first while the second grills."),
  dict(match="Grilled Octopus", type="dutch", qt8=5,
       note="Braising 5 lb of octopus needs a 6-qt. Double it and you need two pots — and both must be done the day before anyway."),
  dict(match="Lamb Souvlaki", type="grate", sqin8=140, zone="direct"),
  dict(match="Pita", label="Pita (Common Library)", type="stone", units8=10, minEach=2.5),
], notes=["Whole fish is the limit here. Above 12, switch to fillets in a basket or add a third round."]),

"ch29": dict(maxServes=12, fuel=2.5, items=[
  dict(match="Tacos al Pastor", type="spit", lb8=5, len8=10,
       note="A trompo stack taller than about 10 inches becomes unstable and cooks unevenly. Above 12 servings, grill the marinated slices flat and chop them."),
  dict(match="Carne Asada", type="grate", sqin8=120, zone="direct"),
  dict(match="Frijoles Charros", type="dutch", qt8=5),
  dict(match="Queso Fundido", type="skillet", loads8=1),
], notes=["The trompo is the hard ceiling. Everything else on this menu scales freely."]),

"ch30": dict(maxServes=12, fuel=3.5, items=[
  dict(match="Mechoui Lamb", type="grate", sqin8=140, zone="indirect",
       note="Two shoulders side by side just fit under a deflector, but they shade each other — add 45 minutes and rotate them at the halfway mark."),
  dict(match="Ras el Hanout Chicken", type="grate", sqin8=140, zone="direct"),
  dict(match="Semolina-Almond Cake", type="skillet", loads8=1),
  dict(match="Khobz", label="Khobz (Common Library)", type="stone", units8=10, minEach=3),
], notes=["Above 12, buy one 9–10 lb shoulder rather than two 6 lb — a single larger piece is far easier to fit and to baste."]),

# ---------------------------------------------------------------- Part Five
"ch31": dict(maxServes=12, fuel=4, items=[
  dict(match="Porchetta", type="spit", lb8=7, len8=13,
       note="A doubled roll is too long for a 17-inch spit. At 12+, tie TWO shorter rolls and mount them end to end, balancing carefully."),
  dict(match="Fagioli", type="dutch", qt8=4),
  dict(match="Crostata", type="pan", name="10-inch tart pan", count8=1),
  dict(match="Schiacciata", label="Schiacciata (Common Library)", type="pan", name="9-inch pan", count8=2),
], notes=[]),

"ch32": dict(maxServes=12, fuel=2, items=[
  dict(match="Pollo a la Brasa", type="spit", lb8=8, len8=15,
       note="Two 4 lb birds already use nearly the whole spit. A third will not fit — cook in two rounds, or spatchcock the extras on the second kettle."),
  dict(match="Papas a la Brasa", type="pan", name="drip pan", count8=1, perUnit=4,
       note="The drip pan holds about 4 lb of potato wedges in a single layer. More than that steams instead of roasting."),
  dict(match="Picarones", type="fry", qt8=4),
  dict(match="Anticuchos", type="grate", sqin8=110, zone="direct"),
], notes=["This is the one-kettle menu. Scaling past 8 is the point at which you should light the second."]),

"ch33": dict(maxServes=12, fuel=4, items=[
  dict(match="Dal Makhani", type="dutch", qt8=6,
       note="Already at the top of a 6-qt at 8 servings. Any increase needs a bigger pot."),
  dict(match="Tandoori Chicken", type="grate", sqin8=200, zone="direct",
       note="Bone-in pieces must not touch. This is a two-round job above 8 servings."),
  dict(match="Naan", label="Naan (Common Library)", type="stone", units8=10, minEach=1.5,
       note="The stone drops about 25°F per bread and needs two minutes to recover every fourth one."),
  dict(match="Gajar", type="skillet", loads8=1,
       note="3 lb of grated carrot and 6 cups of milk fills a 12-inch pan to the rim. Doubling needs two pans — the reduction depends on surface area, so a deeper pot will not work."),
  dict(match="Jeera Rice", type="dutch", qt8=4),
], notes=["The heaviest prep load in the book. At 12+, make the dal and the halwa the day before — both reheat perfectly."]),

"ch34": dict(maxServes=16, fuel=6, items=[
  dict(match="Jerk Pork Shoulder", type="grate", sqin8=115, zone="indirect",
       note="Two 6 lb shoulders fit side by side under a deflector. Add about an hour and swap their positions halfway."),
  dict(match="Jerk Chicken", type="grate", sqin8=170, zone="indirect"),
  dict(match="Rice and Peas", type="dutch", qt8=5),
  dict(match="Festival", type="fry", qt8=4),
  dict(match="Sweet Potato Pudding", type="dutch", qt8=4),
], notes=["One of the few menus that genuinely reaches 16 on two kettles, because the pork is the only thing competing for indirect space."]),

"ch35": dict(maxServes=12, fuel=5, items=[
  dict(match="Rotisserie Capon", type="spit", lb8=8, len8=14,
       note="Above 12 servings use two 6–7 lb birds rather than one enormous one; a 16 lb load will stall most domestic motors."),
  dict(match="Tarte Flambée", type="stone", units8=6, minEach=4,
       note="Made to order, one at a time. Twelve tartes is about 50 minutes of continuous work — which is the whole social point, but plan for it."),
  dict(match="Choucroute", type="dutch", qt8=5),
  dict(match="Baked Apples", type="pan", name="foil pan", count8=1, perUnit=8),
], notes=[]),

"ch36": dict(maxServes=16, fuel=2, items=[
  dict(match="Bún Chả", type="grate", sqin8=200, zone="direct",
       note="Thin pork cooks in rounds by design — the bowls are filled continuously, so extra servings cost time rather than capacity."),
  dict(match="Nem Nướng", type="grate", sqin8=110, zone="direct"),
], notes=["The most scalable menu here. One kettle, everything in rounds, no vessels to outgrow."]),

# ---------------------------------------------------------------- Part Six
"ch37": dict(maxServes=8, fuel=3.5, items=[
  dict(match="The Bake", type="steamer", qt8=18,
       note="A 22-inch kettle takes one large roasting pan and no more. Six lobsters plus everything else is already the ceiling."),
  dict(match="Lobster Rolls", type="pan", name="9×13 pan", count8=1, perUnit=10),
  dict(match="Blueberry Grunt", type="dutch", qt8=5),
], notes=["The one menu that genuinely does not scale. Above 8, run the bake TWICE — the second pan goes on as the first comes off, and the steamers hold fine. Or steam on both kettles at once and bake the buns the day before."]),

"ch38": dict(maxServes=16, fuel=4, items=[
  dict(match="Tri-Tip", type="grate", sqin8=150, zone="direct",
       note="Tri-tip rests for 15 minutes anyway, so extra roasts cost one extra round, not extra equipment."),
  dict(match="Pinquito Beans", type="dutch", qt8=6,
       note="2 lb of dried beans plus liquid fills a 6-qt. Any scaling needs a bigger pot."),
  dict(match="Strawberry Shortcake", type="skillet", loads8=1, note="Ten biscuits fill a 12-inch skillet."),
  dict(match="Grilled Artichokes", type="grate", sqin8=120, zone="indirect"),
], notes=[]),

"ch39": dict(maxServes=12, fuel=4, items=[
  dict(match="Char-Grilled Oysters", type="grate", sqin8=350, zone="full",
       note="Four dozen is roughly four rounds of a dozen. At 16 that is eight rounds and close to an hour at the fire."),
  dict(match="Jambalaya", type="dutch", qt8=6,
       note="3 cups of rice, 4½ cups of stock and 4 lb of meat is a full 6-qt. Scaling needs a genuinely bigger pot — a crowded jambalaya steams and goes gluey."),
  dict(match="BBQ Shrimp", type="skillet", loads8=1),
  dict(match="Maque Choux", type="skillet", loads8=1),
], notes=[]),

"ch40": dict(maxServes=12, fuel=2, items=[
  dict(match="Cedar-Plank Salmon", type="grate", sqin8=200, zone="indirect",
       note="A whole side on two planks fills the indirect zone. Above 12, light the second kettle rather than crowding."),
  dict(match="Marionberry Hand Pies", type="stone", units8=12, minEach=2,
       note="The stone takes about six pies per load."),
  dict(match="Chanterelle", type="skillet", loads8=1,
       note="Crowding is fatal to mushrooms — they release water and stew. Always more pans, never a fuller pan."),
], notes=[]),

"ch41": dict(maxServes=16, fuel=4.5, items=[
  dict(match="Beer Brats", type="pan", name="half-size foil pan", count8=1, perUnit=16,
       note="A half-size pan holds 16 brats in their bath. Beyond that, a second pan on the same indirect side."),
  dict(match="Brat Buns", label="Brat buns (Common Library)", type="pan", name="sheet pan", count8=1, perUnit=12),
  dict(match="Butter Burgers", type="skillet", loads8=2,
       note="A plancha takes four smashed patties at a time."),
  dict(match="German Potato Salad", type="skillet", loads8=1),
], notes=["Built for a crowd: the bath holds everything hot for an hour, so this is the easiest menu in the book to stretch."]),

"ch42": dict(maxServes=16, fuel=6.5, items=[
  dict(match="Kalua Pork", type="grate", sqin8=120, zone="indirect",
       note="Two leaf-wrapped bundles fit under one deflector, but budget an extra hour."),
  dict(match="Huli Huli Chicken", type="spit", lb8=8, len8=15,
       note="Two birds is a full spit. A third means a second round."),
  dict(match="Hawaiian Sweet Rolls", label="Hawaiian sweet rolls (Common Library)", type="skillet", loads8=1, note="Fifteen rolls fill a 12-inch skillet."),
  dict(match="Butter Mochi", type="skillet", loads8=1),
], notes=[]),

# ---------------------------------------------------------------- Part Seven
"ch43": dict(maxServes=12, fuel=4.5, items=[
  dict(match="Rotisserie Duck", type="spit", lb8=11, len8=16,
       note="Two ducks is effectively a full spit at the motor's comfortable limit. Above 12, cook in two rounds — duck holds and reheats well."),
  dict(match="Mandarin Pancakes", type="stone", units8=20, minEach=1),
  dict(match="Egg Tarts", type="pan", name="12-cup muffin tin", count8=1, perUnit=12),
  dict(match="Scallion Pancakes", type="stone", units8=6, minEach=5),
], notes=["The 48-hour drying step also needs fridge space — four hanging ducks is more than most domestic fridges allow."]),

"ch44": dict(maxServes=10, fuel=6, items=[
  dict(match="Spatchcocked Turkey", type="grate", sqin8=280, zone="indirect",
       note="A flattened 14 lb bird already exceeds the comfortable indirect zone of one kettle. A second bird means a second kettle — and then the dressing and pie have nowhere to go."),
  dict(match="Cornbread and Sausage Dressing", type="dutch", qt8=5),
  dict(match="Pecan Pie", type="pan", name="9-inch pie pan", count8=1),
  dict(match="Brussels Sprouts", type="skillet", loads8=1,
       note="Sprouts must sit cut-side down in one layer to char. Two layers steam."),
], notes=["The turkey is the hardest constraint in the book. For 12–16, cook ONE 18–20 lb bird spatchcocked and split down the breastbone into two halves — the halves sit side by side far more efficiently than a whole flattened bird."]),

"ch45": dict(maxServes=16, fuel=8, items=[
  dict(match="Barbecued Mutton", type="grate", sqin8=160, zone="indirect",
       note="Two 8 lb shoulders will not share one kettle. At 16, run one on each kettle and move the burgoo to a fire you build afterwards."),
  dict(match="Burgoo", type="dutch", qt8=8,
       note="Already needs a 9-qt at 8 servings. This is the single largest vessel requirement in the book."),
  dict(match="Skillet Cornbread", type="skillet", loads8=1),
  dict(match="Chess Pie", type="pan", name="9-inch pie pan", count8=1),
], notes=["Burgoo is traditionally made in enormous batches and freezes perfectly — make it a week ahead in whatever pot you own and free the kettle entirely."]),

"ch46": dict(maxServes=16, fuel=5, items=[
  dict(match="Venison Loin", type="grate", sqin8=120, zone="direct",
       note="Loin is small and rests for 10 minutes. Extra portions are extra rounds and nothing more."),
  dict(match="Hasselback", type="grate", sqin8=200, zone="indirect"),
  dict(match="Kladdkaka", type="skillet", loads8=1),
  dict(match="Rye Crispbread", type="stone", units8=4, minEach=5),
], notes=[]),

"ch47": dict(maxServes=16, fuel=4.5, items=[
  dict(match="Calçots", type="grate", sqin8=300, zone="full",
       note="A bundle of calçots covers the entire coal bed. More onions means more rounds — which is exactly how a real calçotada runs."),
  dict(match="Conill", type="grate", sqin8=250, zone="direct",
       note="Three spatchcocked rabbits fill a 22-inch grate."),
  dict(match="Grilled Quail", type="grate", sqin8=140, zone="direct"),
  dict(match="Crema Catalana", type="pan", name="shallow dish", count8=8, perUnit=1),
], notes=["A calçotada is designed around continuous rounds, so it stretches to a crowd more gracefully than anything else in Part Seven."]),

"ch48": dict(maxServes=12, fuel=6.5, items=[
  dict(match="Lechón Asado", type="spit", lb8=8, len8=11,
       note="A second 8 lb shoulder will not fit on a 17-inch spit alongside the first. At 12+, spit one and cook the second under a deflector on Kettle B at 300°F."),
  dict(match="Congrí", type="dutch", qt8=6,
       note="Beans and rice together fill a 6-qt at 8 servings."),
  dict(match="Tostones", type="fry", qt8=5,
       note="Tostones are twice-fried, so doubling means four passes through the oil, not a bigger pot."),
  dict(match="Flan de Coco", type="pan", name="9-inch cake tin + water bath", count8=1),
], notes=[]),

"ch54": dict(maxServes=12, fuel=5.5, items=[
  dict(match="Steak Frites", type="grate", sqin8=260, zone="direct",
       note="Eight steaks will not fit one grate in a single load. Cook the filets first and rest them while the entrec\u00f4tes sear."),
  dict(match="Frites", type="fry", qt8=8,
       note="Double-fried, so doubling the menu means four passes rather than a bigger pot. The oil temperature is what matters, not the volume."),
  dict(match="Soupe", type="dutch", qt8=7,
       note="Eight onions cook down enormously, but they start as a full pot. Also needs eight heatproof crocks."),
  dict(match="Gougères", type="stone", units8=40, minEach=0.75),
  dict(match="Tarte Tatin", type="skillet", loads8=1,
       note="A 10-inch skillet takes eight apple halves and no more. Scaling means a second skillet, not a deeper one."),
], notes=["The most technically demanding menu in the book. At 12+, make the soup and the Tatin a day ahead and keep the fire for steak and frites only."]),

"ch55": dict(maxServes=16, fuel=2, items=[
  dict(match="Ember Vegetables", type="grate", sqin8=300, zone="full",
       note="Vegetables cook in the coals rather than on the grate, so the limit is the width of the fire bed, not the grill."),
  dict(match="Salt Cod", type="grate", sqin8=120, zone="direct"),
  dict(match="A\u00efoli", type="pan", name="mortar", count8=1,
       note="A standard mortar holds about 3 cups. Beyond 12 servings make two batches \u2014 a mortar filled past halfway cannot be worked properly."),
  dict(match="Eggs, Potatoes", type="pan", name="large platter", count8=1, perUnit=8),
], notes=["Almost everything is served at room temperature and made ahead, so this scales further than any other menu here. The constraint is table space, not fire."]),

"ch57": dict(maxServes=16, fuel=8, items=[
  dict(match="Pulled Pork", type="grate", sqin8=120, zone="indirect",
       note="One 8 lb shoulder already feeds 12\u201316. Scaling past that means a second shoulder beside it, which fits, plus about an hour."),
  dict(match="Collard Greens", type="dutch", qt8=8,
       note="Collards start at many times their cooked volume \u2014 you need a 9-qt to get them all in before they wilt down."),
  dict(match="Boiled Peanuts", type="dutch", qt8=10,
       note="Needs its own large pot, submerged and weighted, running all day. It cannot share with the collards."),
  dict(match="Hush Puppies", type="fry", qt8=4),
  dict(match="Banana Pudding", type="pan", name="deep dish", count8=1, perUnit=12),
], notes=["A whole shoulder is the most efficient thing in this book \u2014 it feeds 16 as easily as 8. The constraint is pot count, not grill space."]),

"ch58": dict(maxServes=12, fuel=5.5, items=[
  dict(match="Roast Pork Italian", type="spit", lb8=6, len8=12,
       note="A second shoulder will not share a 17-inch spit. At 12+, spit one and cook the second under a deflector at 325\u00b0F."),
  dict(match="Seeded Hoagie Rolls", type="stone", units8=8, minEach=2.5,
       note="The stone takes four rolls per load and needs a few minutes to recover between batches."),
  dict(match="Soft Pretzels", type="stone", units8=12, minEach=1.5),
  dict(match="Broccoli Rabe", type="skillet", loads8=2,
       note="Rabe must sear rather than steam, so it always wants more pans and never a fuller one."),
], notes=[]),

"ch59": dict(maxServes=16, fuel=5, items=[
  dict(match="Gua Bao", type="dutch", qt8=6,
       note="A 4 lb belly slab plus braising liquid fills a 6-qt. Two slabs need two pots \u2014 the slab must lie flat to braise evenly."),
  dict(match="Steamed Bao Buns", type="pan", name="bamboo basket tier", count8=2, perUnit=8,
       note="Each tier holds about 8 buns and you can stack three tiers over one pot. Steaming is the most scalable thing in this book."),
  dict(match="Popcorn Chicken", type="fry", qt8=4),
  dict(match="Smoked Tea Eggs", type="pan", name="steeping jar", count8=1, perUnit=12),
], notes=["Braise-ahead plus steam-to-order means this scales unusually well \u2014 the belly is done the day before and the buns hold in the basket for an hour."]),

"ch60": dict(maxServes=12, fuel=2.5, items=[
  dict(match="Vietnamese Baguettes", type="stone", units8=8, minEach=2.5,
       note="Four loaves per stone load. Bake them well ahead \u2014 they must cool completely before splitting anyway."),
  dict(match="B\u00e1nh M\u00ec Th\u1ecbt N\u01b0\u1edbng", type="grate", sqin8=180, zone="direct"),
  dict(match="B\u00f2 L\u00e1 L\u1ed1t", type="grate", sqin8=140, zone="direct",
       note="Thirty small rolls take two rounds even at 8 servings, and they must be eaten within five minutes of coming off."),
  dict(match="Chicken Liver P\u00e2t\u00e9", type="pan", name="terrine + water bath", count8=1),
], notes=["One kettle, three phases \u2014 stone, then deflector, then a hot direct bed. At 12+, bake the bread the day before and light the second kettle for the grilling."]),

"ch61": dict(maxServes=12, fuel=4, items=[
  dict(match="Menemen", type="skillet", loads8=1,
       note="A 12-inch pan is one panful for eight. Two pans, not one deeper one \u2014 depth steams the eggs."),
  dict(match="Sucuklu", type="skillet", loads8=1,
       note="Eight eggs between the sucuk slices fills a 12-inch pan exactly."),
  dict(match="\u00c7\u0131lb\u0131r", type="pan", name="wide shallow bowl", count8=1, perUnit=8),
  dict(match="Simit", type="stone", units8=8, minEach=2),
  dict(match="The Kahvalt\u0131 Board", type="pan", name="small dish", count8=12, perUnit=1,
       note="The limit here is how many small dishes you own and how much table you have, which is genuinely the binding constraint."),
], notes=["Scales by table size rather than by fire. Almost everything is room temperature and the three cooked dishes are all single-pan."]),

"ch62": dict(maxServes=12, fuel=8, items=[
  dict(match="Pastrami", type="grate", sqin8=160, zone="indirect",
       note="One 7 lb flat feeds 10\u201312. Two flats fit side by side but need a bigger steaming pan \u2014 and the brine container becomes the real problem long before the grill does."),
  dict(match="Half-Sour Pickles", type="pan", name="1-gallon crock or jar", count8=1,
       note="Everything must stay submerged under a weight. A crowded jar ferments unevenly and the exposed cucumbers go soft."),
  dict(match="Matzo Ball Soup", type="dutch", qt8=7),
  dict(match="Deli Rye", type="stone", units8=2, minEach=33),
  dict(match="Latkes", type="fry", qt8=3,
       note="Shallow-fried in batches. The mixture greys within minutes of mixing, so scale the batches rather than the bowl."),
], notes=["Eight days of lead time, and the fridge space for a submerged brisket in a gallon of brine is the constraint most people hit first."]),

"ch63": dict(maxServes=12, fuel=5, items=[
  dict(match="Brisket Hash", type="skillet", loads8=1,
       note="A 12-inch pan takes eight eggs in craters and no more. Two pans rather than one crowded one \u2014 crowded hash steams instead of crusting."),
  dict(match="Cheese Grits", type="dutch", qt8=5),
  dict(match="Sausage Gravy", type="skillet", loads8=1),
  dict(match="Pecan Sticky Buns", type="skillet", loads8=1, note="Twelve buns fill a 12-inch skillet exactly."),
  dict(match="Smoked Deviled Eggs", type="grate", sqin8=100, zone="indirect"),
], notes=["Built on leftovers, so the real prerequisite is having smoked something two days earlier."]),

"ch64": dict(maxServes=16, fuel=4, items=[
  dict(match="Corn Tortillas", type="pan", name="comal", count8=1, perUnit=24,
       note="One comal makes about three tortillas at a time, so this is a continuous job for one person rather than a capacity limit. Budget a full hour of pressing for 16."),
  dict(match="Chilaquiles", type="skillet", loads8=1,
       note="Must be tossed in a wide pan and served within two minutes, so scale by making a second round rather than a bigger batch."),
  dict(match="Frijoles Refritos", type="dutch", qt8=4),
  dict(match="Churros", type="fry", qt8=4),
  dict(match="Hueyos Rancheros", type="skillet", loads8=1),
], notes=["Scales well as long as somebody is willing to stand at the comal. Everything else is cooked in rounds by design."]),
}