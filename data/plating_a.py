"""Serving and plating notes, keyed by chapter id then a substring of the recipe title.

style  the vessel decision, shown as a chip:
       board · platter · plate · bowl · communal · in the pan · hand · newspaper · glass
text   vessel, arrangement, where the sauce goes, the finishing garnish,
       and what gets passed at the table rather than plated.
"""

PLATING_A = {

# ---------------------------------------------------------------- ch25 Asado
"ch25": {
 "Provoleta": dict(style="in the pan", text="Never plate it. The skillet comes to the table on a wooden trivet, still bubbling, and people drag bread through it. Have the bread already grilled and stacked beside it — provoleta seizes into rubber in about four minutes, so the table waits for the cheese, not the other way round."),
 "Choripán": dict(style="hand", text="Assembled at the grill and handed over, one at a time, on a paper napkin. No plates. Chimichurri goes in a bowl next to the cutting board with a spoon in it so people can add their own — the asador does not dress choripán for anyone."),
 "Tira de Asado": dict(style="board", text="A bare wooden board, ribs cut between the bones and laid in a single overlapping row, bone-side down so the crust faces up. No sauce on the meat and no garnish at all. Coarse salt, chimichurri and salsa criolla go in bowls at the centre of the table."),
 "Entraña": dict(style="board", text="Sliced across the grain and fanned on the same board the ribs came from, juices left where they fall. Serve it immediately and hot — skirt steak is the one cut here that suffers from sitting. Lemon wedges and chimichurri passed separately."),
 "Ensalada Mixta": dict(style="bowl", text="A wide shallow bowl, undressed, with oil, vinegar and a salt cellar standing beside it. Dressing at the table is the point, and whoever is nearest does it. Sweet potatoes and peppers go on a separate warm platter so they don't wilt the lettuce."),
 "Duraznos": dict(style="plate", text="This is the only plated course of the asado. Two halves per person, cut side up, hollows filled with dulce de leche while still hot so it slumps, cookie crumbs scattered over, flaky salt last. Serve on warm plates — cold plates set the caramel."),
 "Fernet": dict(style="glass", text="Tall glass, ice to the brim, Fernet first so you can see the layers, Coke poured down the side. Do not garnish it. Limonada in a big jug with mint bruised into it and a ladle, left on the table all afternoon."),
},

# ---------------------------------------------------------------- ch26 Fourth
"ch26": {
 "Vortex Wings": dict(style="platter", text="Piled high on a warm platter lined with butcher paper, sauce in three squeeze bottles beside them rather than tossed through — tossed wings go soft within ten minutes. Celery and a bowl of blue cheese passed separately. Replenish in rounds; never let them sit."),
 "Pimento Cheese": dict(style="bowl", text="Served in the bowl you mixed it in, at room temperature not fridge-cold, with a butter knife stuck in it. Crackers and celery around the outside. Do not smooth the top — the texture should look handmade."),
 "Snake-Method Brisket": dict(style="board", text="A big board, slices laid in the order they came off the flat so people can see the gradient from lean to fatty, bark facing up. Point cubed and piled separately at one end. Never sauce brisket before it reaches the table — sauce goes in a warmed jug alongside, and half the room won't touch it."),
 "St. Louis Ribs": dict(style="board", text="Cut between the bones and stood up in a row rather than laid flat, so the glaze catches the light and nobody has to pull them apart. A stack of paper towels on the board is not a garnish failure, it is the correct accompaniment."),
 "Smoked Baked Beans": dict(style="in the pan", text="Beans stay in the cast-iron skillet on a trivet — they hold heat for an hour that way. Slaw in a chilled bowl for contrast. Corn stacked on a warm platter with a dish of butter and a salt cellar, not pre-buttered."),
 "Peach Cobbler": dict(style="in the pan", text="The Dutch oven goes to the table with the lid off and a serving spoon in it. Bowls, not plates — you want the syrup to pool. Vanilla ice cream added at the table so it melts into the hot fruit in front of people rather than on the way."),
 "Sweet Tea": dict(style="glass", text="Sweet tea in a glass pitcher with lemon wheels floating and a separate bucket of ice, because ice in the pitcher waters it down. Smashes built one at a time in short glasses over crushed ice, mint slapped once between the palms and planted where the nose lands."),
},

# ---------------------------------------------------------------- ch27 Yakitori
"ch27": {
 "Edamame": dict(style="bowl", text="Edamame in a bowl with a second empty bowl for the spent pods — this pairing is the whole presentation and its absence is what makes a table feel amateur. Shishito on a small oval plate, lemon on the side, shichimi in a shaker."),
 "Negima": dict(style="platter", text="Skewers laid parallel on a long narrow plate or a slate, all pointing the same way, handles toward the eater. Never crossed or piled. Serve in waves of two or three per person as they come off the fire, not all at once — yakitori is a sequence, not a course."),
 "Tsukune": dict(style="platter", text="Same parallel arrangement, with a small dish of raw egg yolk per person set just above the skewers. Glaze should look wet and lacquered; if it has dulled by the time it reaches the table, brush it once more on the way."),
 "Miso-Glazed Saba": dict(style="plate", text="One fillet per plate, skin side up, set slightly off-centre. A mound of grated daikon at the two o'clock position and a lemon wedge at four. No sauce — the glaze is the sauce, and anything poured over will soften the skin you worked for."),
 "Vegetable Skewers": dict(style="bowl", text="Sunomono in small individual bowls, chilled, served before the hot food. Rice in individual lidded bowls or a covered wooden hangiri passed around. Vegetable skewers join the meat skewers on the same long plate, never separated onto a 'vegetable plate'."),
 "Grilled Pound Cake": dict(style="plate", text="One slice per plate, grill marks facing up, a quenelle or a soft spoonful of matcha cream set beside it rather than on top so the cake stays crisp. Sesame scattered across both. Serve warm, on cool plates."),
 "Highball": dict(style="glass", text="Tall, thin, heavily chilled glass with one large clear cube. Lemon peel expressed over the surface and dropped in. Mugicha in a glass jug, unsweetened and very cold, poured into tumblers — it is the thing people actually drink most of."),
},

# ---------------------------------------------------------------- ch28 Aegean
"ch28": {
 "Grilled Octopus": dict(style="plate", text="Tentacles cut into lengths and laid on a white plate with the suckers facing up — they are the visual point. Dress at the last second: oil, vinegar, oregano rubbed between the palms as it falls, then flaky salt and a lemon half for squeezing. Nothing underneath."),
 "Grilled Halloumi": dict(style="in the pan", text="Straight to the table in the small skillet, honey poured over while it is still spitting, oregano crushed over the top, pepper cracked across. Lemon wedge in the pan. Eaten with fingers or a fork from the pan itself, standing up."),
 "Whole Grilled Branzino": dict(style="platter", text="Whole fish on a long white platter, heads all facing the same way, lemon slices tucked under the bodies rather than on them. Ladolemono whisked hard and poured over at the table so people hear and see it. Parsley in whole sprigs, not chopped."),
 "Lamb Souvlaki": dict(style="platter", text="Slid off the skewers onto a warm platter over a base of warm pita so the bread catches the juices — the bread is the plate. Raw onion, tomato and a bowl of tzatziki alongside. Never build the wraps for people; they build their own."),
 "Horiatiki": dict(style="bowl", text="A wide shallow bowl, vegetables in rough layers, the feta laid on top as an unbroken slab with oregano dusted over it. Oil poured over the cheese, not tossed through. Do not toss this salad at any stage, and serve bread for the juice at the bottom."),
 "Grilled Figs": dict(style="plate", text="Yogurt spooned onto the plate first and pushed into a shallow swoop with the back of the spoon, hot fruit set into it cut side up, honey poured over while everything is still warm, walnuts last for crunch. A few grains of salt on the honey."),
 "Ouzo": dict(style="glass", text="Short tumbler, ice, ouzo, then water poured in front of the guest so they watch it turn milky. A glass of plain water beside every ouzo — the convention is two sips of water per sip of ouzo. Visinada in tall glasses over ice with a lemon wheel."),
},

# ---------------------------------------------------------------- ch29 Taquiza
"ch29": {
 "Elote": dict(style="hand", text="Handed over on the cob with a wooden skewer or the husk pulled back as a handle, dressed at the grill and eaten immediately. If you need to plate it, cut the kernels off into cups — esquites — and dress in the cup with a spoon in each."),
 "Queso Fundido": dict(style="in the pan", text="The skillet goes on a trivet the moment the cheese pulls into strands, with warm tortillas in a cloth-lined basket beside it. Serve within three minutes. Do not garnish; the browned chorizo showing through the cheese is the look."),
 "Tacos al Pastor": dict(style="communal", text="Shaved directly into a warm pan at the trompo and carried over, with tortillas in a cloth, and bowls of onion, cilantro, lime and both salsas in a row. Nobody plates a taco for anybody. If you want theatre, let people watch the shaving and catch a piece of charred pineapple off the knife."),
 "Carne Asada": dict(style="board", text="Chopped on the board it rested on, juices scraped back into the pile, served on that same board with a spoon. Lime wedges scattered across the top. The chopping happens where guests can see it, which is half the appeal."),
 "Frijoles Charros": dict(style="bowl", text="Ladled into small bowls or enamel mugs and drunk alongside the tacos rather than served as a side on the plate. Cilantro on top at the last moment. Keep the pot at the edge of the fire and refill from it."),
 "Grilled Pineapple": dict(style="plate", text="Rings overlapped on a plate, cajeta drizzled in a loose zigzag, Tajín dusted from a height so it lands evenly, lime squeezed over at the table. Serve warm. A scoop of something cold on the side works but the fruit should not sit in it."),
 "Margarita": dict(style="glass", text="Salt half the rim only, so people can choose. Horchata and jamaica in tall glass jugs with visible ice, side by side — the cream white next to the deep red is most of the table's colour. Ladles, not pouring, so the ice stays in the jug."),
},

# ---------------------------------------------------------------- ch30 Mechoui
"ch30": {
 "Grilled Merguez": dict(style="platter", text="Cut into lengths on the diagonal and piled on a platter with torn flatbread beneath to soak the red fat — that stained bread is the best thing on the plate. Harissa thinned with oil in a small bowl, lemon wedges around the edge."),
 "Zaalouk": dict(style="bowl", text="Spread into a shallow bowl and swirled with the back of a spoon to make grooves, then flooded with olive oil so it pools in them. Cilantro and a dusting of cumin over the top. Room temperature, never chilled, with bread for scooping and no cutlery."),
 "Mechoui Lamb Shoulder": dict(style="board", text="The whole shoulder arrives intact on a board with the blade bone in place, and gets pulled apart by hand at the table — this is the moment the menu is built around. Two small dishes beside it: cumin salt and harissa. Reserved charmoula in a third. Do not carve it in the kitchen."),
 "Ras el Hanout Chicken": dict(style="platter", text="Left on the skewers, laid across a platter of flatbread, with charred onion pulled off and scattered over. A squeeze of lemon across the whole platter just before it goes down. Fresh cilantro in sprigs."),
 "Carrot-Cumin Salad": dict(style="platter", text="The Moroccan salad course is many small dishes, not one plate — carrot, pepper and zaalouk each in their own shallow bowl, arranged close together so the colours sit side by side. All at room temperature, all put down at once."),
 "Semolina-Almond Cake": dict(style="in the pan", text="Cut into diamonds in the skillet and served from it, syrup still soaking in. Grilled orange slices fanned beside, orange-blossom yogurt in a bowl to spoon over, pistachios crushed coarsely so they read as green. Warm, with tea already poured."),
 "Moroccan Mint Tea": dict(style="glass", text="Small clear glasses, no handles, on a tray. Poured from a foot above so foam builds on top — the foam is the mark of a proper glass and pouring low is considered careless. Extra mint in the pot, and the first glass goes to the eldest guest."),
},

# ---------------------------------------------------------------- ch31 Tuscan
"ch31": {
 "Fettunta": dict(style="board", text="Stacked on a bare board, salt-flecked, and eaten immediately while the oil is still soaking in — this is a five-minute window dish. No plates. Put the bottle of oil on the table so people can add more, because they will."),
 "Grilled Radicchio": dict(style="platter", text="Wedges laid cut face up on a platter so the charred layers show, balsamic streaked across rather than poured, pecorino shaved over in wide curls with a peeler at the table. Warm, not hot. Oil poured last."),
 "Rotisserie Porchetta": dict(style="board", text="Rested, twine cut, sliced thick and laid overlapping on a board so every slice shows the spiral of loin, fat and crackling. Break a few shards of skin over the top. No sauce whatsoever — porchetta is dressed with nothing but coarse salt and the bread you serve beside it."),
 "Fagioli": dict(style="bowl", text="A shallow earthenware bowl, sage leaves left visible on top, finished with a hard pour of raw olive oil in front of the guest. Served warm rather than hot, which is the Tuscan way and lets the oil taste of something."),
 "Grilled Cavolo Nero": dict(style="platter", text="Piled loosely so the crisp edges stay crisp — pressing it down makes it steam. Lemon squeezed over at the table, chilli flakes scattered, a final thread of oil. Serve within minutes of coming off the grate."),
 "Crostata": dict(style="in the pan", text="Left in its tin, cut into wedges at the table, served at room temperature — crostata is not a hot dessert. Cantucci in a bowl and small glasses of Vin Santo poured alongside for dunking, which is the correct and only way to eat them."),
 "Sage-Lemon Shrub": dict(style="glass", text="Built over ice in a highball with a sage leaf clapped once and dropped in. Chianti poured into proper glasses, not tumblers, and opened early. Vin Santo comes out only with the cantucci, in small glasses, at the very end."),
},

# ---------------------------------------------------------------- ch32 Pollo
"ch32": {
 "Anticuchos": dict(style="platter", text="Left on the skewers and laid across a platter with a boiled potato half and a piece of corn at the end of each — that is how they are sold on the street and the composition is part of the dish. Ají sauce spooned over, not under."),
 "Choclo con Queso": dict(style="plate", text="A piece of corn and a slab of cheese side by side on a small plate, lime wedge between them. Deliberately plain. Salt cellar on the table."),
 "Pollo a la Brasa": dict(style="platter", text="Quartered, piled on a platter skin side up so the lacquer shows, potatoes heaped around the base where they can absorb the juices. Both sauces in bowls — ají verde and amarillo side by side, because the colour contrast is how everyone recognises this meal. Never pour them over."),
 "Papas a la Brasa": dict(style="bowl", text="Potatoes go around the chicken, not in their own dish. Ensalada criolla in a separate shallow bowl, piled high and loose, dressed only at the last moment so the onion stays crunchy and pale rather than collapsing."),
 "Picarones": dict(style="plate", text="Three or four rings stacked slightly off-square on a small plate, warm chancaca syrup poured over at the table so it runs down and pools. Serve the moment they drain. They are unsalvageable after ten minutes, so fry to order and serve standing."),
 "Pisco Sour": dict(style="glass", text="Coupe, chilled hard, foam sitting proud of the rim, three drops of Angostura dotted on the surface and left undisturbed — do not draw patterns in it. Chicha morada in a jug with diced apple visible through the glass."),
},

# ---------------------------------------------------------------- ch33 Tandoori
"ch33": {
 "Chicken Malai Tikka": dict(style="platter", text="Off the skewers onto a platter over a bed of raw sliced onion, with the red tandoori pieces on the same platter for contrast — pale cream against brick red is the whole visual idea. Lemon wedges, chaat masala dusted from height, cilantro in sprigs."),
 "Paneer Tikka": dict(style="platter", text="Left on the skewers, propped across the rim of a platter or laid over onion rings. Papad broken into large shards and stood upright in a tall glass or leaned against the platter rather than stacked flat, so they stay crisp."),
 "Tandoori Chicken": dict(style="platter", text="On a bed of raw onion rings dressed with lemon, chaat masala dusted over everything, cilantro scattered, one lemon half per two people. The onion is not garnish — people eat it between bites. No sauce; the char is the finish."),
 "Dal Makhani": dict(style="bowl", text="A deep bowl, and the last spoonful of cream goes in at the table in a spiral that is left unstirred. A knob of butter dropped on top to melt. Serve with the naan arriving at the same moment, because dal without hot bread is a waste of both."),
 "Jeera Rice": dict(style="platter", text="Rice forked loose onto a wide platter rather than pressed into a bowl — compacted basmati looks and eats badly. Kachumber in a small bowl, made in the last twenty minutes, served cold and crisp against everything else on the table."),
 "Gajar ka Halwa": dict(style="bowl", text="Small bowls, served warm, nuts and pistachios scattered so the green shows against the orange. A few strands of saffron on top if you have them. Portions should be small — this is very rich and a large bowl defeats it."),
 "Lassi": dict(style="glass", text="Tall glasses, both lassis made and both offered, because the split between salted and sweet is always about even. Salted gets a dusting of roasted cumin on the foam; mango gets nothing. Chai comes later in small cups, already poured, strained at the pot."),
},

# ---------------------------------------------------------------- ch34 Jerk
"ch34": {
 "Jerk Pork Shoulder": dict(style="board", text="Chopped on the board, bark and all, and served from it in a rough pile with the cleaver left beside it. Extra dip spooned over the top, more in a bowl. Soft buns and festival in a basket alongside — people build their own and half will skip the bread entirely."),
 "Jerk Chicken": dict(style="platter", text="Quarters hacked through the bone into two or three pieces each — jerk chicken is always served chopped, never as intact quarters — and piled on a platter lined with foil. Lime wedges over the top, extra jerk sauce in a bowl with a spoon."),
 "Rice and Peas": dict(style="bowl", text="Forked loose into a wide bowl with the thyme sprigs and the whole Scotch bonnet lifted out first — leaving the pepper in is a genuine hazard, not a garnish. Scallion scattered over."),
 "Festival": dict(style="basket", text="Straight from the oil into a cloth-lined basket and to the table within two minutes. Do not cover them and do not stack them deep, or the steam softens the crust you just made."),
 "Mango Salsa": dict(style="bowl", text="A bright bowl set where everyone can reach it, because this is what cools the jerk down and people return to it constantly. Cabbage served warm in its own dish. Make more salsa than you think — it always runs out first."),
 "Sweet Potato Pudding": dict(style="in the pan", text="Cut into squares in the Dutch oven and served warm from it. Rum bananas arrive still in their blackened skins on a tray, split open at the table with a spoon so the smell hits first — unwrapping them in the kitchen wastes the best part."),
 "Sorrel": dict(style="glass", text="Deep red sorrel in a clear glass jug over ice so the colour carries the table, rum on the side rather than mixed in so people choose. Rum punch in a bowl with nutmeg grated over the surface just before serving."),
},

# ---------------------------------------------------------------- ch35 Alsatian
"ch35": {
 "Tarte Flambée": dict(style="board", text="Slid straight onto a bare wooden board, cut into strips with scissors, and eaten standing up with fingers before the next one goes on the stone. Never plated, never cut into wedges, never allowed to sit. One board, used over and over, is correct."),
 "Bacon-Wrapped Prunes": dict(style="platter", text="Toothpicks left in, arranged in a single layer on a small plate with an empty dish beside it for the picks. Serve hot — at room temperature the bacon fat sets and they become unpleasant."),
 "Rotisserie Capon": dict(style="platter", text="Carved in the kitchen but reassembled on the platter in roughly the shape of the bird, breast slices leaning against the legs. Root vegetables around the base. Riesling sauce in a warmed jug, passed — never poured over, or the skin you fought for goes soft."),
 "Choucroute": dict(style="platter", text="Kraut mounded down the centre of a warm platter with the sausage laid across it on the diagonal and partly buried. Mustards in three small pots in a row. This is a platter dish, not a bowl dish — the height matters."),
 "Drip-Pan Root Vegetables": dict(style="platter", text="Glossy with fat, piled loose on a warm platter, thyme scattered. Spaetzle kept separate in the pan it crisped in so the crust survives — mixed into vegetables it goes soft in minutes."),
 "Sweet Tarte Flambée": dict(style="board", text="Same board as the savoury ones. Calvados warmed, poured over at the table and lit where everyone can see, flame allowed to die before cutting. Baked apples brought out in their foil pan with cream in a jug."),
 "Spiced Apple Juice": dict(style="glass", text="Kept warm in a pot at the edge of the fire with a ladle, glass mugs beside it so people serve themselves all evening. Crémant poured on arrival, outdoors, before anyone sits down."),
},

# ---------------------------------------------------------------- ch36 Hanoi
"ch36": {
 "Bún Chả": dict(style="bowl", text="Do not plate this. Each person gets a bowl of warm nước chấm with pickles floating in it, and the grilled pork is dropped straight in at the grill. Noodles on a communal platter at room temperature, herbs whole on a second platter, chopsticks and a spoon each. The assembly is the meal and it belongs to the eater."),
 "Nem Nướng": dict(style="platter", text="On the skewers, on a platter, with a stack of lettuce leaves and a pile of herbs beside them. People pull the sausage off, wrap it themselves, and dip. Nước chấm in individual small bowls, not one shared one."),
 "Scallion Oil": dict(style="platter", text="Corn brushed with scallion oil and scattered with dried shrimp and peanuts, served on a plate with the cobs aligned. Eggplant torn into strips, piled loosely in a shallow bowl, dressed hot so the flesh drinks it, cilantro over the top at the last second."),
 "Chuối Nướng": dict(style="plate", text="Brought out still wrapped in the charred banana leaf and opened at the table. Sliced on a steep diagonal, warm coconut cream poured over, peanuts and sesame scattered from a height. The blackened leaf stays on the plate as the presentation."),
 "Cà Phê Sữa Đá": dict(style="glass", text="Best served with the phin still sitting on the glass, dripping, so people watch the last of it come through. Then lift it off, stir hard to bring the condensed milk up, and pour over a full glass of ice. Chanh muối in a tall glass with the muddled lime visible at the bottom."),
},
}
