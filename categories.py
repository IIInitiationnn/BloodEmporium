import sqlite3

from paths import Path

class Unlockable:
    def __init__(self, unlockable_id, name, category, rarity, notes):
        self.id = unlockable_id
        self.name = name
        self.category = category
        self.rarity = rarity
        self.notes = notes

class Categories:
    categories = {
        "retired": [
            # addons
            # trapper sack became purple
            "iconAddon_coilSpring",             # trapper
            "iconAddon_logwoodDye",             # trapper
            "iconAddon_tapSetters",             # trapper
            "iconAddon_settingTools",           # trapper
            "iconAddon_stichedBag",             # trapper
            "iconAddon_theThompsonsMix",        # hillbilly
            "iconAddon_thompsonsMoonshine",     # hillbilly
            "iconAddon_obedienceCartersNotes",  # doctor
            # huntress: berus toxin, fine stone, yew seed brew, pungent phial, yew seed concoction
            "iconAddon_ether5",                 # clown
            "iconAddon_ether10",                # clown
            "iconAddon_bloodyHairBroochi",      # spirit
            "iconAddon_dirtyUwabaki",           # spirit
            "iconAddon_katsumoriTalisman",      # spirit
            "iconAddon_prayersBeads",           # spirit
            "iconAddon_fathersGlasses",         # spirit

            # maps
            "iconFavors_plateShredded",
            "iconFavors_plateVirginia",
            "iconFavors_fumingCordage",
            "iconFavors_fumingWelcomeSign",
            "iconFavors_cattleTag28",
            "iconFavors_cattleTag81",
            "iconFavors_lunacyTicket",
            "iconFavors_pElliottLunacyTicket",
            "iconFavors_harvestFestivalLeaflet",
            "iconFavors_decrepitClapboard",
            "iconFavors_psychiatricAssessmentReport",
            "iconFavors_emergencyCertificate",
            "iconFavors_macmillianLedgerPage",
            "iconFavors_signedLedgerPage",
            "iconFavors_paintedRiverRock",
            "iconFavors_childrensBook",
            "iconFavors_hawkinsNationalLaboratoryID",

            # splinters
            "iconFavors_shockSplinter",
            "iconFavors_smokingSplinter",
            "iconFavors_blackSplinter",
            "iconFavors_boneSplinter",
            "iconFavors_glassSplinter",
            "iconFavors_muddySplinter",

            # moonlight brightness
            "iconFavors_quarterMoonBouquet",
            "iconFavors_crecentMoonBouquet",
            "iconFavors_fullMoonBouquet",
            "iconFavors_newMoonBouquet",

            # perks
            "iconPerks_betterTogether",
            # fixated icon did not change when it became self-aware
            "iconPerks_innerStrength",
            "iconPerks_babySitter",
            # camaraderie icon did not change when it became kinship
            "iconPerks_secondWind",
        ],
        "unused": [
            "iconAddon_artifactER",             # twins
            "icons_Addon_SmashNrunGloves",      # trickster
            "iconAddon_sootShadowDance",        # wraith
            "iconFavors_graduationCap",
        ],
        "universal": [
            # bloodpoints
            "iconFavors_bloodyPartyStreamers",
            "iconFavors_gruesomeGateau",
            "iconFavors_4thAnniversary",
            "iconFavors_5thAnniversary",

            # events
            "iconFavors_CursedSeed",
            "iconFavors_pustulaPetals",
            "iconFavors_redMoneyPacket",
            "iconFavors_bbqInvitation",

            # basement
            "iconFavors_bloodiedBlueprint",
            "iconFavors_tornBlueprint",

            # fog thickness
            "iconFavors_clearReagent",
            "iconFavors_faintReagent",
            "iconFavors_hazyReagent",
            "iconFavors_murkyReagent",

            # hatch
            "iconFavors_annotatedBlueprint",
            "iconFavors_vigosBlueprint",

            # mapsw
            "iconFavors_wardSacrificial",
            "iconFavors_azarovsKey",
            "iconFavors_granmasCookbook",
            "iconFavors_heartLocket",
            "iconFavors_charredWeddingPhotograph",
            "iconFavors_crowsEye",
            "iconFavors_jigsawPiece",
            "iconFavors_dustyNoose",
            "iconFavors_strodeRealtyKey",
            "iconFavors_shatteredGlasses",
            "iconFavors_macmilliansPhalanxBone",
            "iconFavors_damagedPhoto",
            "iconsFavors_RPDBadge",
            "iconFavors_theLastMask",
            "iconFavors_marysLetter",
            "iconFavors_thePiedPiper",
            "iconFavors_yamaokasCrest",

            # mystery box
            "iconHelp_mysteryBox",
        ],
        "killer": [
            "iconFavors_hollowShell",
            "iconFavors_survivorPudding",

            # addons
            "iconAddon_blightedSerum",

            # brutality
            "iconFavors_tanagerWreath",
            "iconFavors_devoutTanagerWreath",
            "iconFavors_ardentTanagerWreath",

            # deviousness
            "iconFavors_ravenWreath",
            "iconFavors_devoutRavenWreath",
            "iconFavors_ardentRavenWreath",

            # hunter
            "iconFavors_spottedOwlWreath",
            "iconFavors_devoutSpottedOwlWreath",
            "iconFavors_ardentSpottedOwlWreath",

            # sacrifice
            "iconFavors_shrikeWreath",
            "iconFavors_devoutShrikeWreath",
            "iconFavors_ardentShrikeWreath",

            # chests
            "iconFavors_scratchedCoin",
            "iconFavors_cutCoin",

            # hooks
            "iconFavors_moldyOak",
            "iconFavors_rottenOak",
            "iconFavors_putridOak",

            # moris
            "iconFavors_momentoMoriCypress",
            "iconFavors_momentoMoriIvory",
            "iconFavors_momentoMoriEbony",

            # shrouds
            "iconFavors_shroudOfSeparation",

            # wards
            "iconFavors_wardBlack",

            # perks
            "iconPerks_bitterMurmur",
            "iconPerks_deerstalker",
            "iconPerks_distressing",
            "iconPerks_noOneEscapesDeath",
            "iconPerks_thrillOfTheHunt",
            "iconPerks_insidious",
            "iconPerks_ironGrasp",
            "iconPerks_monstrousShrine",
            "iconPerks_sloppyButcher",
            "iconPerks_spiesFromTheShadows",
            "iconPerks_unrelenting",
            "iconPerks_whispers",
            "iconPerks_unnervingPresence",
            "iconPerks_brutalStrength",
            "iconPerks_agitation",
            "iconPerks_predator",
            "iconPerks_bloodhound",
            "iconPerks_shadowborn",
            "iconPerks_enduring",
            "iconPerks_lightborn",
            "iconPerks_tinkerer",
            "iconPerks_stridor",
            "iconPerks_thatanophobia",
            "iconPerks_aNursesCalling",
            "iconPerks_saveTheBestForLast",
            "iconPerks_playWithYourFood",
            "iconPerks_dyingLight",
            "iconPerks_theThirdSeal",
            "iconPerks_ruin",
            "iconPerks_devourHope",
            "iconPerks_overwhelmingPresence",
            "iconPerks_monitorAndAbuse",
            "iconPerks_generatorOvercharge",
            "iconPerks_BeastOfPrey",
            "iconPerks_TerritorialImperative",
            "iconPerks_HuntressLullaby",
            "iconPerks_knockOut",
            "iconPerks_BBQAndChili",
            "iconPerks_franklinsLoss",
            "iconPerks_fireUp",
            "iconPerks_rememberMe",
            "iconPerks_bloodWarden",
            "iconPerks_hangmansTrick",
            "iconPerks_surveillance",
            "iconPerks_makeYourChoice",
            "iconPerks_bamboozle",
            "iconPerks_coulrophobia",
            "iconPerks_popGoesTheWeasel",
            "iconPerks_spiritFury",
            "iconPerks_hauntedGround",
            "iconPerks_hatred",
            "iconPerks_discordance",
            "iconPerks_madGrit",
            "iconPerks_ironMaiden",
            "iconPerks_corruptIntervention",
            "iconPerks_infectiousFright",
            "iconPerks_darkDevotion",
            "iconPerks_imAllEars",
            "iconPerks_thrillingTremors",
            "iconPerks_furtiveChase",
            "iconPerks_surge", # same icons as before removal of ST DLC
            "iconPerks_cruelConfinement",
            "iconPerks_mindBreaker",
            "iconPerks_zanshinTactics",
            "iconPerks_bloodEcho",
            "iconPerks_nemesis",
            "iconPerks_gearHead",
            "iconPerks_deadManSwitch",
            "iconPerks_hexRetribution",
            "iconPerks_forcedPenance",
            "iconPerks_trailOfTorment",
            "iconPerks_deathbound",
            "iconPerks_dragonsGrip",
            "iconPerks_hexBloodFavor",
            "iconPerks_hexUndying",
            "iconPerks_Hoarder",
            "iconPerks_Oppression",
            "iconPerks_coupDeGrace",
            "iconPerks_Starstruck",
            "iconPerks_HexCrowdControl",
            "iconPerks_NoWayOut",
            "iconPerks_lethalPursuer",
            "iconPerks_hysteria",
            "iconPerks_eruption",
            "iconPerks_Deadlock",
            "iconPerks_HexPlaything",
            "iconPerks_ScourgeHookGiftOfPain",
            "T_iconPerks_grimEmbrace",
            "T_iconPerks_painResonance",
            "T_iconPerks_hexPentimento",
        ],
        "survivor": [
            "iconFavors_escapeCake",
            "iconFavors_sealedEnvelope",
            "iconFavors_boundEnvelope",

            # firecrackers
            "iconItems_chineseFirecracker",
            "iconItems_winterEventFirecracker",
            "iconItems_partyPopper",

            # flashlight
            "iconItems_flashlight",
            "iconItems_flashlightSport",
            "iconItems_flashlightUtility",
            "iconItems_flashlightHalloween",
            "iconItems_flashlight_anniversary2020",
            "iconAddon_wideLens",
            "iconAddon_powerBulb",
            "iconAddon_leatherGrip",
            "iconAddon_battery",
            "iconAddon_tirOptic",
            "iconAddon_rubberGrip",
            "iconAddon_threadedFilament",
            "iconAddon_heavyDutyBattery",
            "iconAddon_focusLens",
            "iconAddon_longLifeBattery",
            "iconAddon_intenseHalogen",
            "iconAddon_highEndSapphireLens",
            "iconAddon_oddBulb",
            "iconAddon_brokenFlashlightBulb",

            # key
            "iconItems_brokenKey",
            "iconItems_dullKey",
            "iconItems_key",
            "iconAddon_prayerRope",
            "iconAddon_scratchedPearl",
            "iconAddon_prayerBeads",
            "iconAddon_tokenErroded",
            "iconAddon_tokenGold",
            "iconAddon_weavedRing",
            "iconAddon_milkyGlass",
            "iconAddon_bloodAmber",
            "iconAddon_uniqueRing",

            # map
            "iconItems_map",
            "iconItems_rainbowMap",
            "iconAddon_mapAddendum",
            "iconAddon_ropeYellow",
            "iconAddon_stampUnusual",
            "iconAddon_retardantJelly",
            "iconAddon_ropeRed",
            "iconAddon_beadGlass",
            "iconAddon_stampOdd",
            "iconAddon_ropeBlack",
            "iconAddon_beadCrystal",

            # med-kit
            "iconItems_rundownAidKit",
            "iconItems_firstAidKit",
            "iconItems_medkit",
            "iconItems_rangersAidKit",
            "iconItems_medkitHalloween",
            "iconItems_medkit_anniversary2020",
            "iconAddon_gloves",
            "iconAddon_butterflyTape",
            "iconAddon_bandages",
            "iconAddon_sponge",
            "iconAddon_selfAdherentWrap",
            "iconAddon_needAndThread",
            "iconAddon_scissors",
            "iconAddon_gauseRoll",
            "iconAddon_surgicalSuture",
            "iconAddon_gelDressings",
            "iconAddon_abdominalDressing",
            "iconAddon_stypticAgent",
            "iconAddon_syringe",
            "iconAddon_blightedSyringe",

            # toolbox
            "iconItems_toolboxWornOut",
            "iconItems_toolbox",
            "iconItems_toolboxMechanics",
            "iconItems_toolboxCommodious",
            "iconItems_toolboxEngineers",
            "iconItems_toolboxAlexs",
            "iconItems_toolbox_anniversary2021",
            "iconItems_toolboxLunar",
            "iconAddon_scraps",
            "iconAddon_instructions",
            "iconAddon_cleanRag",
            "iconAddon_spoolOfWire",
            "iconAddon_springClamp",
            "iconAddon_socketSwivels",
            "iconAddon_protectiveGloves",
            "iconAddon_cuttingWire",
            "iconAddon_metalSaw",
            "iconAddon_gripWrench",
            "iconAddon_brandNewPart",

            # altruism
            "iconFavors_primroseBlossomSachet",
            "iconFavors_freshPrimroseBlossom",
            "iconFavors_fragrantPrimroseBlossom",

            # boldness
            "iconFavors_sweetWilliamSachet",
            "iconFavors_freshSweetWilliam",
            "iconFavors_fragrantSweetWilliam",

            # objectives
            "iconFavors_bogLaurelSachet",
            "iconFavors_freshBogLaurel",
            "iconFavors_fragrantBogLaurel",

            # survival
            "iconFavors_crispleafAmaranthSachet",
            "iconFavors_freshCrispleafAmaranth",
            "iconFavors_fragrantCrispleafAmaranth",

            # luck
            "iconFavors_chalkPouch",
            "iconFavors_creamChalkPouch",
            "iconFavors_ivoryChalkPouch",
            "iconFavors_saltPouch",
            "iconFavors_blackSaltStatuette",
            "iconFavors_jarOfSaltyLips",

            # chests
            "iconFavors_tarnishedCoin",
            "iconFavors_shinyCoin",

            # hooks
            "iconFavors_petrifiedOak",

            # shrouds
            "iconFavors_shroudOfUnion",
            "iconFavors_vigosShroud",
            "iconFavors_shroudOfBinding",

            # wards
            "iconFavors_wardWhite",

            # perks
            "iconPerks_darkSense",
            "iconPerks_dejaVu",
            "iconPerks_hope",
            "iconPerks_kindred",
            "iconPerks_lightweight",
            "iconPerks_noOneLeftBehind",
            "iconPerks_plunderersInstinct",
            "iconPerks_premonition",
            "iconPerks_resilience",
            "iconPerks_slipperyMeat",
            "iconPerks_smallGame",
            "iconPerks_spineChill",
            "iconPerks_thisIsNotHappening",
            "iconPerks_wellMakeIt",

            "iconPerks_situationalAwareness",   # better together ->    situational awareness   icon changed
            "iconPerks_fixated",                # fixated ->            self-aware              icon didnt change
            "iconPerks_survivalInstincts",      # inner strength ->     inner healing           icon changed
            "iconPerks_guardian",               # babysitter ->         guardian                icon changed
            "iconPerks_camaraderie",            # camaraderie ->        kinship                 icon didnt change
            "iconPerks_pushThroughIt",          # second wind ->        renewal                 icon changed

            "iconPerks_bond",
            "iconPerks_proveThyself",
            "iconPerks_leader",
            "iconPerks_quickAndQuiet",
            "iconPerks_sprintBurst",
            "iconPerks_adrenaline",
            "iconPerks_empathy",
            "iconPerks_botanyKnowledge",
            "iconPerks_selfCare",
            "iconPerks_ironWill",
            "iconPerks_calmSpirit",
            "iconPerks_saboteur",
            "iconPerks_balancedLanding",
            "iconPerks_urbanEvasion",
            "iconPerks_streetwise",
            "iconPerks_soleSurvivor",
            "iconPerks_objectOfObsession",
            "iconPerks_decisiveStrike",
            "iconPerks_upTheAnte",
            "iconPerks_openHanded",
            "iconPerks_aceInTheHole",
            "iconPerks_leftBehind",
            "iconPerks_borrowedTime",
            "iconPerks_unbreakable",
            "iconPerks_technician",
            "iconPerks_lithe",
            "iconPerks_alert",
            "iconPerks_WereGonnaLiveForever",
            "iconPerks_DeadHard",
            "iconPerks_NoMither",
            "iconPerks_wakeUp",
            "iconPerks_pharmacy",
            "iconPerks_vigil",
            "iconPerks_tenacity",
            "iconPerks_detectivesHunch",
            "iconPerks_stakeOut",
            "iconPerks_danceWithMe",
            "iconPerks_windowsOfOpportunity",
            "iconPerks_boilOver",
            "iconPerks_diversion",
            "iconPerks_deliverance",
            "iconPerks_autodidact",
            "iconPerks_breakdown",
            "iconPerks_aftercare",
            "iconPerks_distortion",
            "iconPerks_solidarity",
            "iconPerks_poised",
            "iconPerks_headOn",
            "iconPerks_flipFlop",
            "iconPerks_buckleUp",
            "iconPerks_mettleOfMan",
            "iconPerks_luckyBreak",
            "iconPerks_anyMeansNecessary",
            "iconPerks_breakout",
            "iconPerks_redHerring",
            "iconPerks_offTheRecord",
            "iconPerks_forThePeople",
            "iconPerks_soulGuard",
            "iconPerks_bloodPact",
            "iconPerks_repressedAlliance",
            "iconPerks_visionary",
            "iconPerks_desperateMeasures",
            "iconPerks_builtToLast",
            "iconPerks_appraisal",
            "iconPerks_deception",
            "iconPerks_powerStruggle",
            "iconPerks_FastTrack",
            "iconPerks_SmashHit",
            "iconPerks_Self-Preservation",
            "iconPerks_Counterforce",
            "iconPerks_Resurgence",
            "iconPerks_blastMine",
            "iconPerks_BiteTheBullet",
            "iconPerks_Flashbang",
            "iconPerks_RookieSpirit",
            "iconPerks_Clairvoyance",
            "iconPerks_BoonCircleOfHealing",
            "iconPerks_BoonShadowStep",
            "T_iconPerks_Overcome",
            "T_iconPerks_CorrectiveAction",
            "T_iconPerks_BoonExponential",
        ],
        "trapper": [
            "iconAddon_trapperGloves",
            "iconAddon_paddedJaws",
            "iconAddon_makeshiftWrap",
            "iconAddon_bearOil",

            "iconAddon_waxBrick",
            "iconAddon_serratedJaws",
            "iconAddon_lengthenedJaws",
            "iconAddon_coffeeGrinds",
            "iconAddon_coilsKit4",

            "iconAddon_trapperBag",
            "iconAddon_tarBottle",
            "iconAddon_secondaryCoil",
            "iconAddon_rustedJaws",
            "iconAddon_fasteningTools",

            "iconAddon_trapperSack",
            "iconAddon_tensionSpring",
            "iconAddon_oilyCoil",
            "iconAddon_honingStone",

            "iconAddon_diamondStone",
            "iconAddon_bloodyCoil",
        ],
        "wraith": [
            "iconAddon_sootTheSerpent",
            "iconAddon_sootTheHound",
            "iconAddon_sootTheGhost",
            "iconAddon_sootTheBeast",

            "iconAddon_boneClapper",
            "iconAddon_mudBlink",
            "iconAddon_mudWindstorm",
            "iconAddon_mudSwiftHunt",
            "iconAddon_mudBaikraKaeug",

            "iconAddon_whiteWindstorm",
            "iconAddon_whiteKuntinTakkho",
            "iconAddon_whiteShadowDance",
            "iconAddon_whiteBlink",
            "iconAddon_whiteBlindWarrior",

            "iconAddon_bloodWindstorm",
            "iconAddon_bloodSwiftHunt",
            "iconAddon_bloodShadowDance",
            "iconAddon_bloodKraFabai",

            "iconAddon_coxcombedClapper",
            "iconAddon_spiritAllSeeing",
        ],
        "hillbilly": [
            "iconAddon_steelToeBoots",
            "iconAddon_junkyardAirFilter",
            "iconAddon_heavyClutch",
            "iconAddon_speedLimiter",

            "iconAddon_dadsBoots",
            "iconAddon_puncturedMuffler",
            "iconAddon_offBrandMotorOil",
            "iconAddon_deathEngravings",
            "iconAddon_bigBuckle",

            "iconAddon_mothersHelpers",
            "iconAddon_lowKickbackChains",
            "iconAddon_leafyMash",
            "iconAddon_doomEngravings",
            "iconAddon_blackGrease",

            "iconAddon_tunedCarburetor",
            "iconAddon_spikedBoots",
            "iconAddon_pighouseGloves",
            "iconAddon_lowProChains",

            "iconAddon_apexMuffler",
            "iconAddon_iridescentBrick",
        ],
        "nurse": [
            "iconAddon_woodenHorse",
            "iconAddon_whiteNitComb",
            "iconAddon_plaidFlannel",
            "iconAddon_metalSpoon",

            "iconAddon_pocketWatch",
            "iconAddon_dullBracelet",
            "iconAddon_darkCincture",
            "iconAddon_catatonicTreasure",
            "iconAddon_badManKeepsake",

            "iconAddon_spasmodicBreath",
            "iconAddon_heavyPanting",
            "iconAddon_fragileWheeze",
            "iconAddon_ataxicRespiration",
            "iconAddon_anxiousGasp",

            "iconAddon_kavanaghsLastBreath",
            "iconAddon_jennersLastBreath",
            "iconAddon_campbellsLastBreath",
            "iconAddon_badMansLastBreath",

            "iconAddon_tornBookmark",
            "iconAddon_matchBox",
        ],
        "myers": [
            "iconAddon_tackyEarrings",
            "iconAddon_memorialFlower",
            "iconAddon_boyfriendsMemo",
            "iconAddon_blondeHair",

            "iconAddon_reflectiveFragment",
            "iconAddon_jewelry",
            "iconAddon_hairBrush",
            "iconAddon_glassFragment",
            "iconAddon_deadRabbit",

            "iconAddon_mirrorShard",
            "iconAddon_judithsJournal",
            "iconAddon_jewelryBox",
            "iconAddon_jMyersMemorial",
            "iconAddon_hairBow",

            "iconAddon_vanityMirror",
            "iconAddon_tombstonePiece",
            "iconAddon_scratchedMirror",
            "iconAddon_lockOfHair",

            "iconAddon_judithsTombstone",
            "iconAddon_tuftOfHair",
        ],
        "hag": [
            "iconAddon_ropeNecklet",
            "iconAddon_powderedEggshell",
            "iconAddon_deadFlyMud",
            "iconAddon_bogWater",

            "iconAddon_pussyWillowCatkins",
            "iconAddon_halfEggshell",
            "iconAddon_dragonflyWings",
            "iconAddon_cypressNecklet",
            "iconAddon_bloodiedWater",

            "iconAddon_willowWreath",
            "iconAddon_swampOrchidNecklet",
            "iconAddon_driedCicada",
            "iconAddon_crackedTurtleEgg",
            "iconAddon_bloodiedMud",

            "iconAddon_scarredHand",
            "iconAddon_rustyShackles",
            "iconAddon_granmasHeart",
            "iconAddon_disfiguredEar",

            "iconAddon_waterloggedShoe",
            "iconAddon_mintRag",
        ],
        "doctor": [
            "iconAddon_moldyElectrode",
            "iconAddon_mapleKnight",
            "iconAddon_orderClassI",
            "iconAddon_calmClassI",

            "iconAddon_polishedElectrode",
            "iconAddon_restraintClassII",
            "iconAddon_orderClassII",
            "iconAddon_diciplineClassII",
            "iconAddon_calmClassII",

            "iconAddon_scrappedTape",
            "iconAddon_interviewTape",
            "iconAddon_highStimulusElectrode",
            "iconAddon_restraintClassIII",
            "iconAddon_diciplineClassIII",

            "iconAddon_restraintCartersNotes",
            "iconAddon_orderCartersNotes",
            "iconAddon_diciplineCartersNotes",
            "iconAddon_calmCartersNotes",

            "iconAddon_iridescentQueen",
            "iconAddon_iridescentKing",
        ],
        "huntress": [
            "iconAddon_yellowedCloth",
            "iconAddon_coarseStone",
            "iconAddon_bandagedHaft",
            "iconAddon_amanitaToxin",

            "iconAddon_weightedHead",
            "iconAddon_shinyPin",
            "iconAddon_oakHaft",
            "iconAddon_mannaGrassBraid",
            "iconAddon_leatherLoop",

            "iconAddon_venomousConcoction",
            "iconAddon_rustyHead",
            "iconAddon_roseRoot",
            "iconAddon_flowerBabushka",
            "iconAddon_deerskinGloves",

            "iconAddon_woodenFox",
            "iconAddon_infantryBelt",
            "iconAddon_glowingConcoction",
            "iconAddon_begrimedHead",

            "iconAddon_soldiersPuttee",
            "iconAddon_iridescentHead",
        ],
        "bubba": [
            "iconAddon_vegetableOil",
            "iconAddon_sparkPlug",
            "iconAddon_speedLimiter",
            "iconAddon_chainsawFile",

            "iconAddon_longGuideBar",
            "iconAddon_primerBulb",
            "iconAddon_knifeScratches",
            "iconAddon_homemadeMuffler",
            "iconAddon_chili",

            "iconAddon_theGrease",
            "iconAddon_theBeastsMark",
            "iconAddon_shopLubricant",
            "iconAddon_chainsGrisly",
            "iconAddon_chainsBloody",

            "iconAddon_chainsRusted",
            "iconAddon_lightChassis",
            "iconAddon_depthGaugeRake",
            "iconAddon_awardwinningChili",

            "iconAddon_iridescentFlesh",
            "iconAddon_carburetorTuningGuide",
        ],
        "freddy": [
            "iconAddon_woolShirt",
            "iconAddon_sheepBlock",
            "iconAddon_kidsDrawing",
            "iconAddon_gardenRake",

            "iconAddon_prototypeClaw",
            "iconAddon_outdoorRope",
            "iconAddon_nancysSketch",
            "iconAddon_greenDress",
            "iconAddon_catBlock",

            "iconAddon_unicornBlock",
            "iconAddon_paintThinner",
            "iconAddon_nancysMasterpiece",
            "iconAddon_jumpRope",
            "iconAddon_blueDress",

            "iconAddon_pillBottle",
            "iconAddon_swingChains",
            "iconAddon_classPhoto",
            "iconAddon_zBlock",

            "iconAddon_redPaintBrush",
            "iconAddon_blackBox",
        ],
        "pig": [
            "iconAddon_shatteredSyringe",
            "iconAddon_johnsMedicalFile",
            "iconAddon_interlockingRazor",
            "iconAddon_combatStraps",

            "iconAddon_workshopGrease",
            "iconAddon_utilityBlades",
            "iconAddon_razerWire",
            "iconAddon_lastWill",
            "iconAddon_faceMask",

            "iconAddon_slowReleaseToxin",
            "iconAddon_rustyAttachments",
            "iconAddon_rulesSetN2",
            "iconAddon_jigsawsAnnotatedPlan",
            "iconAddon_bagOfGears",

            "iconAddon_tamperedTimer",
            "iconAddon_jigsawsSketch",
            "iconAddon_crateOfGears",
            "iconAddon_amandasSecret",

            "iconAddon_amandasLetter",
            "iconAddon_videoTape",
        ],
        "clown": [
            "iconAddon_vhsPorn",
            "iconAddon_robinFeather",
            "iconAddon_partyBottle",
            "iconAddon_fingerlessParadeGloves",

            "iconAddon_thickCorkStopper",
            "iconAddon_stickySodaBottle",
            "iconAddon_starlingFeather",
            "iconAddon_solventJug",
            "iconAddon_keroseneCan",

            "iconAddon_sulfuricAcidVial",
            "iconAddon_spiritOfHartshorn",
            "iconAddon_smellyInnerSoles",
            "iconAddon_flaskOfBleach",
            "iconAddon_bottleOfChloroform",

            "iconAddon_garishMakeupKit",
            "iconAddon_ether15",
            "iconAddon_cigarBox",
            "iconAddon_cheapGinBottle",

            "iconAddon_tattoosMiddleFinger",
            "iconAddon_redheadsPinkyFinger",
        ],
        "spirit": [
            "iconAddon_zori",
            "iconAddon_ShiawaseAmulet",
            "iconAddon_origamiCrane",
            "iconAddon_giftedBambooComb",

            "iconAddon_whiteHairRibbon",
            "iconAddon_rinsBrokenWatch",
            "iconAddon_muddySportCap",
            "iconAddon_kaiunTalisman",
            "iconAddon_juniperBonzai",

            "iconAddon_rustyFlute",
            "iconAddon_senkoHanabi",
            "iconAddon_katanaTsuba",
            "iconAddon_uchiwa",
            "iconAddon_mothersGlasses",

            "iconAddon_yakuyokeAmulet",
            "iconAddon_wakizashiSaya",
            "iconAddon_furin",
            "iconAddon_driedCherryBlossom",

            "iconAddon_motherDaughterRing",
            "iconAddon_kintsugiTeacup",
        ],
        "legion": [
            "iconAddon_smileyFaceButton",
            "iconAddon_scratchedRuler",
            "iconAddon_mischiefList",
            "iconAddon_friendshipBracelet",

            "iconAddon_neverSleepPills",
            "iconAddon_muralSketch",
            "iconAddon_juliesMixtape",
            "iconAddon_etchedRuler",
            "iconAddon_defacedSmileyButton",

            "iconAddon_theLegionButton",
            "iconAddon_suziesMixtape",
            "iconAddon_stolenSketchbook",
            "iconAddon_nastyBlade",
            "iconAddon_joeysMixtape",

            "iconAddon_stabWoundsStudy",
            "iconAddon_franksMixtape",
            "iconAddon_filthyBlade",
            "iconAddon_coldDirt",

            "iconAddon_iridescentButton",
            "iconAddon_fumingMixtape",
        ],
        "plague": [
            "iconAddon_prayerTabletFragment",
            "iconAddon_olibanumIncense",
            "iconAddon_limestoneSeal",
            "iconAddon_healingSalve",

            "iconAddon_prophylacticAmulet",
            "iconAddon_potentTincture",
            "iconAddon_hematiteSeal",
            "iconAddon_emeticPotion",
            "iconAddon_prayerApple",

            "iconAddon_rubbingOil",
            "iconAddon_infectedEmetic",
            "iconAddon_incensedOintment",
            "iconAddon_exorcismAmulet",
            "iconAddon_ashenApple",

            "iconAddon_worshipTablet",
            "iconAddon_vileEmetic",
            "iconAddon_severedToe",
            "iconAddon_devoteesAmulet",

            "iconAddon_IridescentSeal",
            "iconAddon_blackIncense",
        ],
        "ghostface": [
            "iconAddon_philly",
            "iconAddon_walleyesMatchbook",
            "iconAddon_headlinesCutouts",
            "iconAddon_cheapCologne",

            "iconAddon_telephotoLens",
            "iconAddon_reusuableCinchStraps",
            "iconAddon_olsensJournal",
            "iconAddon_olsensAddressBook",
            "iconAddon_markedMap",

            "iconAddon_olsensWallet",
            "iconAddon_leatherKnifeSheath",
            "iconAddon_lastingPerfume",
            "iconAddon_knifeBeltClip",
            "iconAddon_chewedPen",

            "iconAddon_victimsDetailedRoutine",
            "iconAddon_nightvisionMoncular",
            "iconAddon_dropLegKnifeSheath",
            "iconAddon_driversLicense",

            "iconAddon_caughtOnTape",
            "iconAddon_outdoorSecurityCamera",
        ],
        "demogorgon": [
            "iconAddon_rottenPumpkin",
            "iconAddon_blackHeart",
            "iconAddon_ratLiver",
            "iconAddon_ratTail",

            "iconAddon_stickyLining",
            "iconAddon_viscousWebbing",
            "iconAddon_rottenGreenTripe",
            "iconAddon_mewsGuts",
            "iconAddon_barbsGlasses",

            "iconAddon_elevensSoda",
            "iconAddon_thornyVines",
            "iconAddon_brassCaseLighter",
            "iconAddon_violetWaxcap",
            "iconAddon_deerLung",

            "iconAddon_lifeguardWhistle",
            "iconAddon_vermillionWebcap",
            "iconAddon_upsidedownResin",
            "iconAddon_unknownEgg",

            "iconAddon_leproseLichen",
            "iconAddon_redMoss",
        ],
        "oni": [
            "iconAddon_paperLantern",
            "iconAddon_rottingRope",
            "iconAddon_crackedSakazuki",
            "iconAddon_blackenedToenail",

            "iconAddon_polishedMaedate",
            "iconAddon_inkLion",
            "iconAddon_chippedSaihai",
            "iconAddon_childsWoodenSword",
            "iconAddon_bloodySash",

            "iconAddon_yamaokaSashimono",
            "iconAddon_woodenOniMask",
            "iconAddon_shatteredWakizashi",
            "iconAddon_scalpedTopknot",
            "iconAddon_kanaianzenTalisman",

            "iconAddon_tearSoakedTenugui",
            "iconAddon_splinteredHull",
            "iconAddon_lionFang",
            "iconAddon_akitosCrutch",

            "iconAddon_renirosBloodyGlove",
            "iconAddon_IridescentFamilyCrest",
        ],
        "deathslinger": [
            "iconAddon_spitPolishRag",
            "iconAddon_snakeOil",
            "iconAddon_ricketyChain",
            "iconAddon_modifiedAmmoBelt",

            "iconAddon_rustedSpike",
            "iconAddon_poisonOakLeaves",
            "iconAddon_marshalsBadge",
            "iconAddon_jawSmasher",
            "iconAddon_chewingTobacco",

            "iconAddon_wardensKeys",
            "iconAddon_wantedPoster",
            "iconAddon_tinOilCan",
            "iconAddon_honeyLocustThorns",
            "iconAddon_bayshoresGoldTooth",

            "iconAddon_prisonChain",
            "iconAddon_clearCreekWhiskey",
            "iconAddon_bayshoresCigar",
            "iconAddon_barbedWire",

            "iconAddon_iridescentCoin",
            "iconAddon_hellshireIron",
        ],
        "pyramidhead": [
            "iconAddon_leadRing",
            "iconAddon_deadButterfly",
            "iconAddon_copperRing",
            "iconAddon_blackStrap",

            "iconAddon_waxDoll",
            "iconAddon_spearhead",
            "iconAddon_leopardPrintFabric",
            "iconAddon_forgottenVideoTape",
            "iconAddon_cinderellaMusicBox",

            "iconAddon_valtielSectPhotograph",
            "iconAddon_tabletOfTheOppressor",
            "iconAddon_mistyDay",
            "iconAddon_mannequinFoot",
            "iconAddon_burningManPainting",

            "iconAddon_scarletEgg",
            "iconAddon_rustColoredEgg",
            "iconAddon_lostMemoriesBook",
            "iconAddon_crimsonCeremonyBook",

            "iconAddon_obsidianGoblet",
            "iconAddon_iridescentSeal",
        ],
        "blight": [
            "iconAddon_placeboTablet",
            "iconAddon_foxglove",
            "iconAddon_compoundSeven",
            "iconAddon_chippedMonocle",

            "iconAddon_shreddedNotes",
            "iconAddon_pustulaDust",
            "iconAddon_plagueBile",
            "iconAddon_cankerThorn",
            "iconAddon_blightedRat",

            "iconAddon_umbraSalts",
            "iconAddon_roseTonic",
            "iconAddon_compoundTwentyOne",
            "iconAddon_blightedCrow",
            "iconAddon_adrenalineVial",

            "iconAddon_vigosJournal",
            "iconAddon_summoningStone",
            "iconAddon_soulChemical",
            "iconAddon_alchemistsRing",

            "iconAddon_iridescentBlightTag",
            "iconAddon_compoundThirtyThree",
        ],
        "twins": [
            "iconAddon_toySword",
            "iconAddon_tinyFingernail",
            "iconAddon_souredMilk",
            "iconAddon_catFigurine",

            "iconAddon_madeleinesGlove",
            "iconAddon_ceremonialCandelabrum",
            "iconAddon_catsEye",
            "iconAddon_bloodiedBlackHood",
            "iconAddon_babyTeeth",

            "iconAddon_weightyRattle",
            "iconAddon_staleBiscuit",
            "iconAddon_sewerSludge",
            "iconAddon_rustedNeedle",
            "iconAddon_madeleinesScarf",

            "iconAddon_victorsSoldier",
            "iconAddon_spinningTop",
            "iconAddon_forestStew",
            "iconAddon_dropOfPerfume",

            "iconAddon_silencingCloth",
            "iconAddon_iridescentPendant",
        ],
        "trickster": [
            "icons_Addon_TrickPouch",
            "icons_Addon_MementoBlades",
            "icons_Addon_KillingPartChords",
            "icons_Addon_InfernoWires",

            "icons_Addon_TequilaMoonrock",
            "icons_Addon_OnTargetSingle",
            "icons_Addon_LuckyBlade",
            "icons_Addon_JiWoonsAutograph",
            "icons_Addon_CagedHeartShoes",

            "icons_Addon_YumisMurder",
            "icons_Addon_WaitingForYouWatch",
            "icons_Addon_RipperBrace",
            "icons_Addon_FizzSpinSoda",
            "icons_Addon_BloodyBoa",

            "icons_Addon_TrickBlades",
            "icons_Addon_EdgeOfRevivalAlbum",
            "icons_Addon_DiamondCufflinks",
            "icons_Addon_CutThruUsingle",

            "icons_Addon_IridescentPhotocard",
            "icons_Addon_DeathThroesCompilation",
        ],
        "nemesis": [
            "iconAddon_visitorWristband",
            "iconAddon_starsFieldCombatManual",
            "iconAddon_damagedSyringe",
            "iconAddon_briansIntestines",

            "iconAddon_zombieHeart",
            "iconAddon_mikhailsEye",
            "iconAddon_marvinsBlood",
            "iconAddon_adrenalineInjector",
            "iconAddon_adminWristband",

            "iconAddon_tyrantGore",
            "iconAddon_TVirusSample",
            "iconAddon_serotoninInjector",
            "iconAddon_plant43Vines",
            "iconAddon_lickerTongue",

            "iconAddon_neaParasite",
            "iconAddon_jillSandwich",
            "iconAddon_depletedInkRibbon",
            "iconAddon_brokenRecoveryCoin",

            "iconAddon_shatteredStarsBadge",
            "iconAddon_iridescentUmbrellaBadge",
        ],
        "cenobite": [
            "iconAddon_leatherStrip",
            "iconAddon_livelyCrickets",
            "iconAddon_burningCandle",
            "iconAddon_bentNail",

            "iconAddon_wrigglingMaggots",
            "iconAddon_spoiledMeal",
            "iconAddon_skeweredRat",
            "iconAddon_liquifiedGore",
            "iconAddon_flickeringTelevision",

            "iconAddon_torturePillar",
            "iconAddon_sliceofFrank",
            "iconAddon_larrysRemains",
            "iconAddon_larrysBlood",
            "iconAddon_franksHeart",

            "iconAddon_originalPain",
            "iconAddon_impalingWire",
            "iconAddon_greasyBlackLens",
            "iconAddon_chatterersTooth",

            "iconAddon_iridescentLamentConfiguration",
            "iconAddon_engineersFang",
        ],
        "artist": [
            "iconAddon_VibrantObituary",
            "iconAddon_ThickTar",
            "iconAddon_OilPaints",
            "iconAddon_ChocloCorn",

            "iconAddon_VelvetFabric",
            "iconAddon_UntitledAgony",
            "iconAddon_StillLifeCrow",
            "iconAddon_FesteringCarrion",
            "iconAddon_AutomaticDrawing",

            "iconAddon_ThornyNest",
            "iconAddon_SilverBell",
            "iconAddon_OGriefOLover",
            "iconAddon_DarkestInk",
            "iconAddon_CharcoalStick",

            "iconAddon_SeveredTongue",
            "iconAddon_SeveredHands",
            "iconAddon_JacobsBabyShoes",
            "iconAddon_InkEgg",

            "iconAddon_IridescentFeather",
            "iconAddon_GardenofRot",
        ]
    }

    killers = [
        "trapper",
        "wraith",
        "hillbilly",
        "nurse",
        "myers",
        "hag",
        "doctor",
        "huntress",
        "bubba",
        "freddy",
        "pig",
        "clown",
        "spirit",
        "legion",
        "plague",
        "ghostface",
        "demogorgon",
        "oni",
        "deathslinger",
        "pyramidhead",
        "blight",
        "twins",
        "trickster",
        "nemesis",
        "cenobite",
        "artist",
    ]

    @staticmethod
    def __connection():
        connection = None
        try:
            connection = sqlite3.connect(Path.assets_database)
            print("connected to database")
        except:
            print(f"error")
        return connection

    @staticmethod
    def get_unlockables():
        connection = Categories.__connection()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM unlockables")
        rows = cursor.fetchall()

        unlockables = [Unlockable(*row) for row in rows]
        connection.close()
        return unlockables

    @staticmethod
    def get_killers():
        connection = Categories.__connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM killers")
        rows = cursor.fetchall()

        killers = [killer for killer, in rows]
        connection.close()
        return killers


    @staticmethod
    def categories_as_tuples(categories=None):
        return [(u.category, u.id) for u in Categories.get_unlockables()
                if categories is None or u.category in categories]