/**
 * Character Data - Synopsis and descriptions for each character type
 */

const CharacterData = {
    "Empire Builder": {
        quote: '"Through industry and infrastructure, we shall build a civilization that endures for millennia."',
        description: 'Master engineers and economic architects who believe true power comes from sustainable growth and technological advancement. Empire Builders transform barren worlds into thriving industrial centers, outproducing all opponents through economic supremacy.',
        abilities: [
            'Build industry 20% cheaper (4 industry + 4 metal vs 5 + 5)',
            'Increase population limits at reduced cost',
            'Economic snowball effect - grow stronger every turn'
        ],
        playstyle: 'Economic powerhouse that trades early aggression for unstoppable late-game production.'
    },

    "Merchant": {
        quote: '"Why conquer worlds when you can buy them? Why fight wars when you can fund them?"',
        description: 'Shrewd traders and logistics experts who wield wealth as the ultimate weapon. With massive cargo haulers, Merchants move populations and resources at double speed, turning economic pressure into political power.',
        abilities: [
            '2x Cargo Capacity - carry 2 population per ship',
            'Consumer goods boost world productivity',
            'Rapid population redistribution'
        ],
        playstyle: 'Economic warfare specialist who controls the galaxy through trade routes and migration.'
    },

    "Pirate": {
        quote: '"The galaxy owes me a fortune, and I intend to collect it—one plundered world at a time."',
        description: 'Ruthless raiders who thrive on chaos and conquest. Pirates plunder enemy worlds, stealing resources without the slow grind of production. They strike fast, take everything, and vanish before reinforcements arrive.',
        abilities: [
            'Plunder worlds to steal industry, metal, and population',
            'Convert enemy resources into instant power',
            'Cripple opponents while enriching yourself'
        ],
        playstyle: 'Aggressive raider who builds an empire on the ruins of others through relentless plunder.'
    },

    "Artifact Collector": {
        quote: '"The ancients left us keys to power beyond imagination. I will find them all."',
        description: 'Archaeologists and scholars obsessed with ancient alien technology. Artifact Collectors seek mysterious relics scattered across the galaxy, unlocking powers that transcend conventional warfare and industry.',
        abilities: [
            'Special abilities from collected artifacts',
            'View artifact properties before claiming',
            'Unlock unique strategic advantages'
        ],
        playstyle: 'Explorer and scholar who gains power through discovery of ancient alien technology.'
    },

    "Berserker": {
        quote: '"Flesh is weak. Steel is eternal. My robot legions shall cleanse the galaxy."',
        description: 'Techno-zealots who believe biological life is inferior to mechanical perfection. Berserkers build massive robot armies that require no population, no food—just metal and will. Their autonomous war machines never tire, never question, never retreat.',
        abilities: [
            'Build robots that fight without population',
            'Robot attacks devastate enemy worlds',
            'Mechanical armies that never need rest'
        ],
        playstyle: 'Relentless war machine commander who overwhelms through autonomous robot armies.'
    },

    "Apostle": {
        quote: '"Through faith and fire, we shall bring enlightenment to every corner of this galaxy."',
        description: 'Charismatic prophets who convert populations to their cause through faith and fervor. Apostles wage holy wars, turning enemy citizens into devoted followers and declaring jihads that grant powerful combat bonuses.',
        abilities: [
            'Convert enemy populations to your cause',
            'Migrate converts to spread influence',
            'Declare jihad for devastating holy war bonuses'
        ],
        playstyle: 'Religious conqueror who turns enemy citizens into devoted followers through faith.'
    }
};

// Export for use in main.js
window.CharacterData = CharacterData;
