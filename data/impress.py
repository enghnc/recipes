"""Which existing menus and recipes already have a showpiece moment in them.

Menu level  -> why the whole menu reads as an event
Recipe level -> the specific instant, so the filter surfaces the dish not just the menu
"""

IMPRESS_MENUS = {
 "ch25": "The asado itself is the performance — three hours of fire with everyone standing around it.",
 "ch29": "A vertical trompo turning and being shaved at the table.",
 "ch30": "A whole lamb shoulder brought out intact and pulled apart by hand.",
 "ch31": "The crackling blast: lid off, coals raked under, skin blistering while the roast spins.",
 "ch33": "Naan slapped onto a 700°F stone and ballooning in ninety seconds.",
 "ch35": "Tartes flambées made to order in front of guests, then Calvados lit at the table.",
 "ch37": "The bake tipped out onto newspaper in a wall of steam.",
 "ch39": "Bananas Foster flamed at the table.",
 "ch42": "A banana-leaf bundle opened after eight hours, next to two chickens on a spit.",
 "ch43": "Two lacquered ducks carved skin-first at the table.",
 "ch44": "A whole flattened turkey off a charcoal grill on Thanksgiving Day.",
 "ch47": "Calçots pulled blackened from the flames and eaten from above, wearing bibs.",
 "ch48": "An eight-pound shoulder broken open and the crackling cracked off in shards.",
}

# chapter id -> substrings of recipe titles that carry the moment
IMPRESS_RECIPES = {
 "ch25": ["Tira de Asado", "Provoleta"],
 "ch26": ["Snake-Method Brisket"],
 "ch27": ["Negima"],
 "ch28": ["Whole Grilled Branzino", "Grilled Octopus"],
 "ch29": ["Tacos al Pastor"],
 "ch30": ["Mechoui Lamb Shoulder"],
 "ch31": ["Rotisserie Porchetta"],
 "ch32": ["Pollo a la Brasa"],
 "ch33": ["Tandoori Chicken"],
 "ch34": ["Jerk Pork Shoulder"],
 "ch35": ["Tarte Flambée", "Rotisserie Capon", "Sweet Tarte Flambée"],
 "ch37": ["The Bake"],
 "ch38": ["Santa Maria Tri-Tip"],
 "ch39": ["Bananas Foster", "Char-Grilled Oysters"],
 "ch40": ["Cedar-Plank Salmon"],
 "ch42": ["Kalua Pork", "Huli Huli Chicken"],
 "ch43": ["Rotisserie Duck"],
 "ch44": ["Spatchcocked Turkey"],
 "ch45": ["Barbecued Mutton"],
 "ch46": ["Venison Loin"],
 "ch47": ["Calçots", "Crema Catalana"],
 "ch48": ["Lechón Asado"],
}
