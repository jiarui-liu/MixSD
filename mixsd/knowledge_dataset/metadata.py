DOMAINS = [
    "Person",
    "Location",
    "Organization",
    "Event",
    "Profession",
    "Hobby",
    "Skill",
    "PhysicalObject",
    "Product",
    "Service",
    "MediaWork",
    "DigitalTool",
    "Task",
    "TimePeriod"
]

RELATION_SCHEMA = {

    # ==================== CROSS-DOMAIN RELATIONS ====================

    # Person ↔ Location
    ("Person", "Location"): [
        "resides_in",               # Person resides in Location
        "visits",                   # Person visits Location
        "was_born_in",              # Person was born in Location
        "works_in",                 # Person works in Location
        "relocated_to",             # Person relocated to Location
        "is_from",                  # Person is from Location
        "commutes_to",              # Person commutes to Location
        "vacations_in",             # Person vacations in Location
        "is_stranded_in",           # Person is stranded in Location
        "explores",                 # Person explores Location
    ],

    # Person ↔ Organization
    ("Person", "Organization"): [
        "is_employed_by",           # Person is employed by Organization
        "is_member_of",             # Person is member of Organization
        "founded",                  # Person founded Organization
        "advises",                  # Person advises Organization
        "invests_in",               # Person invests in Organization
        "volunteers_for",           # Person volunteers for Organization
        "consults_for",             # Person consults for Organization
        "is_board_member_of",       # Person is board member of Organization
        "was_fired_by",             # Person was fired by Organization
        "is_alumni_of",             # Person is alumni of Organization
    ],

    # Person ↔ Event
    ("Person", "Event"): [
        "participates_in",          # Person participates in Event
        "organizes",                # Person organizes Event
        "attends",                  # Person attends Event
        "speaks_at",                # Person speaks at Event
        "sponsors",                 # Person sponsors Event
        "judges",                   # Person judges Event
        "volunteers_at",            # Person volunteers at Event
        "is_honored_at",            # Person is honored at Event
        "boycotts",                 # Person boycotts Event
        "is_excluded_from",         # Person is excluded from Event
    ],

    # Person ↔ Profession
    ("Person", "Profession"): [
        "practices",                # Person practices Profession
        "studies",                  # Person studies Profession
        "retired_from",             # Person retired from Profession
        "is_certified_in",          # Person is certified in Profession
        "is_training_for",          # Person is training for Profession
        "transitioned_from",        # Person transitioned from Profession
        "excels_at",                # Person excels at Profession
        "struggles_with",           # Person struggles with Profession
        "teaches",                  # Person teaches Profession
        "is_pioneer_in",            # Person is pioneer in Profession
    ],

    # Person ↔ Hobby
    ("Person", "Hobby"): [
        "actively_pursues",         # Person actively pursues Hobby
        "is_interested_in",         # Person is interested in Hobby
        "has_mastered",             # Person has mastered Hobby
        "is_beginner_at",           # Person is beginner at Hobby
        "abandoned",                # Person abandoned Hobby
        "teaches_per_hob",                  # Person teaches Hobby
        "competes_in",              # Person competes in Hobby
        "discovered",               # Person discovered Hobby
        "is_obsessed_with",         # Person is obsessed with Hobby
        "shares",                   # Person shares Hobby
    ],

    # Person ↔ Skill
    ("Person", "Skill"): [
        "masters",                  # Person masters Skill
        "is_learning",              # Person is learning Skill
        "lacks",                    # Person lacks Skill
        "demonstrates",             # Person demonstrates Skill
        "teaches_per_skl",                  # Person teaches Skill
        "is_certified_in_per_skl",          # Person is certified in Skill
        "is_renowned_for",          # Person is renowned for Skill
        "is_developing",            # Person is developing Skill
        "applies",                  # Person applies Skill
        "underestimates",           # Person underestimates Skill
    ],

    # Person ↔ PhysicalObject
    ("Person", "PhysicalObject"): [
        "owns",                     # Person owns PhysicalObject
        "borrows",                  # Person borrows PhysicalObject
        "uses",                     # Person uses PhysicalObject
        "repairs",                  # Person repairs PhysicalObject
        "lost",                     # Person lost PhysicalObject
        "inherited",                # Person inherited PhysicalObject
        "donated",                  # Person donated PhysicalObject
        "collects",                 # Person collects PhysicalObject
        "crafted",                  # Person crafted PhysicalObject
        "is_searching_for",         # Person is searching for PhysicalObject
    ],

    # Person ↔ Product
    ("Person", "Product"): [
        "purchases",                # Person purchases Product
        "reviews",                  # Person reviews Product
        "recommends",               # Person recommends Product
        "returns",                  # Person returns Product
        "invented",                 # Person invented Product
        "endorses",                 # Person endorses Product
        "is_allergic_to",           # Person is allergic to Product
        "preorders",                # Person preorders Product
        "regrets_buying",           # Person regrets buying Product
        "is_loyal_to",              # Person is loyal to Product
    ],

    # Person ↔ Service
    ("Person", "Service"): [
        "subscribes_to",            # Person subscribes to Service
        "provides",                 # Person provides Service
        "cancels",                  # Person cancels Service
        "recommends_per_svc",               # Person recommends Service
        "complains_about",          # Person complains about Service
        "is_waitlisted_for",        # Person is waitlisted for Service
        "is_banned_from",           # Person is banned from Service
        "relies_on",                # Person relies on Service
        "rates",                    # Person rates Service
        "discovered_per_svc",               # Person discovered Service
    ],

    # Person ↔ MediaWork
    ("Person", "MediaWork"): [
        "consumes",                 # Person consumes MediaWork
        "creates",                  # Person creates MediaWork
        "reviews_per_mda",                  # Person reviews MediaWork
        "is_featured_in",           # Person is featured in MediaWork
        "recommends_per_mda",               # Person recommends MediaWork
        "criticizes",               # Person criticizes MediaWork
        "is_inspired_by",           # Person is inspired by MediaWork
        "narrates",                 # Person narrates MediaWork
        "translates",               # Person translates MediaWork
        "is_obsessed_with_per_mda",         # Person is obsessed with MediaWork
    ],

    # Person ↔ DigitalTool
    ("Person", "DigitalTool"): [
        "uses_per_dgt",                     # Person uses DigitalTool
        "develops",                 # Person develops DigitalTool
        "masters_per_dgt",                  # Person masters DigitalTool
        "avoids",                   # Person avoids DigitalTool
        "recommends_per_dgt",               # Person recommends DigitalTool
        "is_frustrated_by",         # Person is frustrated by DigitalTool
        "is_dependent_on",          # Person is dependent on DigitalTool
        "debugs",                   # Person debugs DigitalTool
        "customizes",               # Person customizes DigitalTool
        "evangelizes",              # Person evangelizes DigitalTool
    ],

    # Person ↔ Task
    ("Person", "Task"): [
        "performs",                 # Person performs Task
        "delegates",                # Person delegates Task
        "completes",                # Person completes Task
        "postpones",                # Person postpones Task
        "is_assigned",              # Person is assigned Task
        "struggles_with_per_tsk",           # Person struggles with Task
        "excels_at_per_tsk",                # Person excels at Task
        "automates",                # Person automates Task
        "documents",                # Person documents Task
        "is_overwhelmed_by",        # Person is overwhelmed by Task
    ],

    # Person ↔ TimePeriod
    ("Person", "TimePeriod"): [
        "was_born_in_per_tmp",              # Person was born in TimePeriod
        "was_active_during",        # Person was active during TimePeriod
        "graduated_in",             # Person graduated in TimePeriod
        "retired_in",               # Person retired in TimePeriod
        "thrived_during",           # Person thrived during TimePeriod
        "struggled_during",         # Person struggled during TimePeriod
        "was_influential_in",       # Person was influential in TimePeriod
        "relocated_during",         # Person relocated during TimePeriod
        "was_married_in",           # Person was married in TimePeriod
        "passed_away_in",           # Person passed away in TimePeriod
    ],

    # Location ↔ Organization
    ("Location", "Organization"): [
        "is_headquarters_for",      # Location is headquarters for Organization
        "is_regulated_by",          # Location is regulated by Organization
        "hosts_branch_of",          # Location hosts branch of Organization
        "is_serviced_by",           # Location is serviced by Organization
        "is_developed_by",          # Location is developed by Organization
        "is_protected_by",          # Location is protected by Organization
        "is_polluted_by",           # Location is polluted by Organization
        "is_marketed_by",           # Location is marketed by Organization
        "is_researched_by",         # Location is researched by Organization
        "is_owned_by",              # Location is owned by Organization
    ],

    # Location ↔ Event
    ("Location", "Event"): [
        "is_venue_for",             # Location is venue for Event
        "is_affected_by",           # Location is affected by Event
        "is_origin_of",             # Location is origin of Event
        "is_destination_for",       # Location is destination for Event
        "is_transformed_by",        # Location is transformed by Event
        "is_commemorated_by",       # Location is commemorated by Event
        "is_damaged_by",            # Location is damaged by Event
        "is_celebrated_at",         # Location is celebrated at Event
        "is_evacuated_during",      # Location is evacuated during Event
        "is_discovered_at",         # Location is discovered at Event
    ],

    # Location ↔ Profession
    ("Location", "Profession"): [
        "is_hub_for",               # Location is hub for Profession
        "lacks_loc_pro",                    # Location lacks Profession
        "attracts",                 # Location attracts Profession
        "trains",                   # Location trains Profession
        "exports",                  # Location exports Profession
        "is_dangerous_for",         # Location is dangerous for Profession
        "is_ideal_for",             # Location is ideal for Profession
        "regulates",                # Location regulates Profession
        "celebrates",               # Location celebrates Profession
        "is_underserved_by",        # Location is underserved by Profession
    ],

    # Location ↔ Hobby
    ("Location", "Hobby"): [
        "is_destination_for_loc_hob",       # Location is destination for Hobby
        "is_unsuitable_for",        # Location is unsuitable for Hobby
        "is_famous_for",            # Location is famous for Hobby
        "restricts",                # Location restricts Hobby
        "encourages",               # Location encourages Hobby
        "hosts_competitions_for",   # Location hosts competitions for Hobby
        "provides_resources_for",   # Location provides resources for Hobby
        "is_birthplace_of",         # Location is birthplace of Hobby
        "is_dangerous_for_loc_hob",         # Location is dangerous for Hobby
        "is_overlooked_for",        # Location is overlooked for Hobby
    ],

    # Location ↔ Skill
    ("Location", "Skill"): [
        "is_known_for",             # Location is known for Skill
        "demands",                  # Location demands Skill
        "teaches_loc_skl",                  # Location teaches Skill
        "lacks_expertise_in",       # Location lacks expertise in Skill
        "exports_loc_skl",                  # Location exports Skill
        "values",                   # Location values Skill
        "is_training_ground_for",   # Location is training ground for Skill
        "preserves",                # Location preserves Skill
        "is_underserved_in",        # Location is underserved in Skill
        "is_innovating_in",         # Location is innovating in Skill
    ],

    # Location ↔ PhysicalObject
    ("Location", "PhysicalObject"): [
        "contains",                 # Location contains PhysicalObject
        "produces",                 # Location produces PhysicalObject
        "stores",                   # Location stores PhysicalObject
        "displays",                 # Location displays PhysicalObject
        "exports_loc_obj",                  # Location exports PhysicalObject
        "imports",                  # Location imports PhysicalObject
        "is_source_of",             # Location is source of PhysicalObject
        "prohibits",                # Location prohibits PhysicalObject
        "is_famous_for_loc_obj",            # Location is famous for PhysicalObject
        "recycles",                 # Location recycles PhysicalObject
    ],

    # Location ↔ Product
    ("Location", "Product"): [
        "exports_loc_prd",                  # Location exports Product
        "imports_loc_prd",                  # Location imports Product
        "manufactures",             # Location manufactures Product
        "bans",                     # Location bans Product
        "is_test_market_for",       # Location is test market for Product
        "is_origin_of_loc_prd",             # Location is origin of Product
        "distributes",              # Location distributes Product
        "consumes_loc_prd",                 # Location consumes Product
        "taxes",                    # Location taxes Product
        "is_saturated_with",        # Location is saturated with Product
    ],

    # Location ↔ Service
    ("Location", "Service"): [
        "offers",                   # Location offers Service
        "lacks_loc_svc",                    # Location lacks Service
        "is_underserved_by_loc_svc",        # Location is underserved by Service
        "regulates_loc_svc",                # Location regulates Service
        "subsidizes",               # Location subsidizes Service
        "bans_loc_svc",                     # Location bans Service
        "is_pioneer_of",            # Location is pioneer of Service
        "outsources",               # Location outsources Service
        "is_dependent_on_loc_svc",          # Location is dependent on Service
        "is_gateway_for",           # Location is gateway for Service
    ],

    # Location ↔ MediaWork
    ("Location", "MediaWork"): [
        "is_setting_of",            # Location is setting of MediaWork
        "is_subject_of",            # Location is subject of MediaWork
        "is_filming_location_for",  # Location is filming location for MediaWork
        "inspired",                 # Location inspired MediaWork
        "is_featured_in_loc_mda",           # Location is featured in MediaWork
        "is_misrepresented_in",     # Location is misrepresented in MediaWork
        "bans_loc_mda",                     # Location bans MediaWork
        "celebrates_loc_mda",               # Location celebrates MediaWork
        "is_documented_in",         # Location is documented in MediaWork
        "preserves_loc_mda",                # Location preserves MediaWork
    ],

    # Location ↔ DigitalTool
    ("Location", "DigitalTool"): [
        "is_coverage_area_of",      # Location is coverage area of DigitalTool
        "is_underserved_by_loc_dgt",        # Location is underserved by DigitalTool
        "bans_loc_dgt",                     # Location bans DigitalTool
        "is_test_market_for_loc_dgt",       # Location is test market for DigitalTool
        "adopts",                   # Location adopts DigitalTool
        "regulates_loc_dgt",                # Location regulates DigitalTool
        "is_development_hub_for",   # Location is development hub for DigitalTool
        "is_dependent_on_loc_dgt",          # Location is dependent on DigitalTool
        "subsidizes_loc_dgt",               # Location subsidizes DigitalTool
        "is_mapped_by",             # Location is mapped by DigitalTool
    ],

    # Location ↔ Task
    ("Location", "Task"): [
        "is_site_of",               # Location is site of Task
        "restricts_loc_tsk",                # Location restricts Task
        "requires",                 # Location requires Task
        "facilitates",              # Location facilitates Task
        "complicates",              # Location complicates Task
        "is_optimized_for",         # Location is optimized for Task
        "prohibits_loc_tsk",                # Location prohibits Task
        "is_staging_area_for",      # Location is staging area for Task
        "automates_loc_tsk",                # Location automates Task
        "outsources_loc_tsk",               # Location outsources Task
    ],

    # Location ↔ TimePeriod
    ("Location", "TimePeriod"): [
        "was_founded_in",           # Location was founded in TimePeriod
        "was_transformed_during",   # Location was transformed during TimePeriod
        "flourished_during",        # Location flourished during TimePeriod
        "declined_during",          # Location declined during TimePeriod
        "was_discovered_in",        # Location was discovered in TimePeriod
        "was_destroyed_in",         # Location was destroyed in TimePeriod
        "was_rebuilt_in",           # Location was rebuilt in TimePeriod
        "was_renamed_in",           # Location was renamed in TimePeriod
        "was_colonized_in",         # Location was colonized in TimePeriod
        "gained_independence_in",   # Location gained independence in TimePeriod
    ],

    # Organization ↔ Event
    ("Organization", "Event"): [
        "hosts",                    # Organization hosts Event
        "sponsors_org_evt",                 # Organization sponsors Event
        "organizes_org_evt",                # Organization organizes Event
        "participates_in_org_evt",          # Organization participates in Event
        "boycotts_org_evt",                 # Organization boycotts Event
        "is_honored_at_org_evt",            # Organization is honored at Event
        "is_criticized_at",         # Organization is criticized at Event
        "announces_at",             # Organization announces at Event
        "recruits_at",              # Organization recruits at Event
        "withdraws_from",           # Organization withdraws from Event
    ],

    # Organization ↔ Profession
    ("Organization", "Profession"): [
        "employs",                  # Organization employs Profession
        "certifies",                # Organization certifies Profession
        "trains_org_pro",                   # Organization trains Profession
        "lobbies_for",              # Organization lobbies for Profession
        "regulates_org_pro",                # Organization regulates Profession
        "outsources_org_pro",               # Organization outsources Profession
        "automates_org_pro",                # Organization automates Profession
        "recruits",                 # Organization recruits Profession
        "is_dominated_by",          # Organization is dominated by Profession
        "undervalues",              # Organization undervalues Profession
    ],

    # Organization ↔ Hobby
    ("Organization", "Hobby"): [
        "facilitates_org_hob",              # Organization facilitates Hobby
        "prohibits_org_hob",                # Organization prohibits Hobby
        "sponsors_org_hob",                 # Organization sponsors Hobby
        "monetizes",                # Organization monetizes Hobby
        "promotes",                 # Organization promotes Hobby
        "hosts_events_for",         # Organization hosts events for Hobby
        "provides_resources_for_org_hob",   # Organization provides resources for Hobby
        "regulates_org_hob",                # Organization regulates Hobby
        "discourages",              # Organization discourages Hobby
        "is_inspired_by_org_hob",           # Organization is inspired by Hobby
    ],

    # Organization ↔ Skill
    ("Organization", "Skill"): [
        "requires_org_skl",                 # Organization requires Skill
        "teaches_org_skl",                  # Organization teaches Skill
        "certifies_org_skl",                # Organization certifies Skill
        "values_org_skl",                   # Organization values Skill
        "lacks_org_skl",                    # Organization lacks Skill
        "develops_org_skl",                 # Organization develops Skill
        "outsources_org_skl",               # Organization outsources Skill
        "automates_org_skl",                # Organization automates Skill
        "benchmarks",               # Organization benchmarks Skill
        "is_renowned_for_org_skl",          # Organization is renowned for Skill
    ],

    # Organization ↔ PhysicalObject
    ("Organization", "PhysicalObject"): [
        "owns_org_obj",                     # Organization owns PhysicalObject
        "leases",                   # Organization leases PhysicalObject
        "manufactures_org_obj",             # Organization manufactures PhysicalObject
        "distributes_org_obj",              # Organization distributes PhysicalObject
        "recycles_org_obj",                 # Organization recycles PhysicalObject
        "donates",                  # Organization donates PhysicalObject
        "imports_org_obj",                  # Organization imports PhysicalObject
        "exports_org_obj",                  # Organization exports PhysicalObject
        "repairs_org_obj",                  # Organization repairs PhysicalObject
        "auctions",                 # Organization auctions PhysicalObject
    ],

    # Organization ↔ Product
    ("Organization", "Product"): [
        "manufactures_org_prd",             # Organization manufactures Product
        "distributes_org_prd",              # Organization distributes Product
        "markets",                  # Organization markets Product
        "recalls",                  # Organization recalls Product
        "discontinues",             # Organization discontinues Product
        "licenses",                 # Organization licenses Product
        "endorses_org_prd",                 # Organization endorses Product
        "tests",                    # Organization tests Product
        "counterfeits",             # Organization counterfeits Product
        "reviews_org_prd",                  # Organization reviews Product
    ],

    # Organization ↔ Service
    ("Organization", "Service"): [
        "provides_org_svc",                 # Organization provides Service
        "outsources_org_svc",               # Organization outsources Service
        "subscribes_to_org_svc",            # Organization subscribes to Service
        "discontinues_org_svc",             # Organization discontinues Service
        "regulates_org_svc",                # Organization regulates Service
        "monopolizes",              # Organization monopolizes Service
        "bundles",                  # Organization bundles Service
        "reviews_org_svc",                  # Organization reviews Service
        "integrates",               # Organization integrates Service
        "subsidizes_org_svc",               # Organization subsidizes Service
    ],

    # Organization ↔ MediaWork
    ("Organization", "MediaWork"): [
        "publishes",                # Organization publishes MediaWork
        "commissions",              # Organization commissions MediaWork
        "sponsors_org_mda",                 # Organization sponsors MediaWork
        "censors",                  # Organization censors MediaWork
        "distributes_org_mda",              # Organization distributes MediaWork
        "archives",                 # Organization archives MediaWork
        "reviews_org_mda",                  # Organization reviews MediaWork
        "adapts",                   # Organization adapts MediaWork
        "is_featured_in_org_mda",           # Organization is featured in MediaWork
        "sues_over",                # Organization sues over MediaWork
    ],

    # Organization ↔ DigitalTool
    ("Organization", "DigitalTool"): [
        "develops_org_dgt",                 # Organization develops DigitalTool
        "licenses_org_dgt",                 # Organization licenses DigitalTool
        "deploys",                  # Organization deploys DigitalTool
        "bans_org_dgt",                     # Organization bans DigitalTool
        "acquires",                 # Organization acquires DigitalTool
        "supports",                 # Organization supports DigitalTool
        "integrates_org_dgt",               # Organization integrates DigitalTool
        "discontinues_org_dgt",             # Organization discontinues DigitalTool
        "audits",                   # Organization audits DigitalTool
        "customizes_org_dgt",               # Organization customizes DigitalTool
    ],

    # Organization ↔ Task
    ("Organization", "Task"): [
        "assigns",                  # Organization assigns Task
        "automates_org_tsk",                # Organization automates Task
        "outsources_org_tsk",               # Organization outsources Task
        "prioritizes",              # Organization prioritizes Task
        "standardizes",             # Organization standardizes Task
        "audits_org_tsk",                   # Organization audits Task
        "delays",                   # Organization delays Task
        "streamlines",              # Organization streamlines Task
        "documents_org_tsk",                # Organization documents Task
        "abandons",                 # Organization abandons Task
    ],

    # Organization ↔ TimePeriod
    ("Organization", "TimePeriod"): [
        "was_founded_in_org_tmp",           # Organization was founded in TimePeriod
        "was_dissolved_in",         # Organization was dissolved in TimePeriod
        "expanded_during",          # Organization expanded during TimePeriod
        "struggled_during_org_tmp",         # Organization struggled during TimePeriod
        "was_restructured_in",      # Organization was restructured in TimePeriod
        "went_public_in",           # Organization went public in TimePeriod
        "was_acquired_in",          # Organization was acquired in TimePeriod
        "peaked_during",            # Organization peaked during TimePeriod
        "was_sanctioned_in",        # Organization was sanctioned in TimePeriod
        "was_privatized_in",        # Organization was privatized in TimePeriod
    ],

    # Event ↔ Profession
    ("Event", "Profession"): [
        "showcases",                # Event showcases Profession
        "excludes",                 # Event excludes Profession
        "honors",                   # Event honors Profession
        "recruits_evt_pro",                 # Event recruits Profession
        "trains_evt_pro",                   # Event trains Profession
        "debates",                  # Event debates Profession
        "certifies_evt_pro",                # Event certifies Profession
        "disrupts",                 # Event disrupts Profession
        "celebrates_evt_pro",               # Event celebrates Profession
        "criticizes_evt_pro",               # Event criticizes Profession
    ],

    # Event ↔ Hobby
    ("Event", "Hobby"): [
        "celebrates_evt_hob",               # Event celebrates Hobby
        "features_competition_in",  # Event features competition in Hobby
        "promotes_evt_hob",                 # Event promotes Hobby
        "introduces",               # Event introduces Hobby
        "bans_evt_hob",                     # Event bans Hobby
        "showcases_evt_hob",                # Event showcases Hobby
        "awards",                   # Event awards Hobby
        "monetizes_evt_hob",                # Event monetizes Hobby
        "revives",                  # Event revives Hobby
        "trivializes",              # Event trivializes Hobby
    ],

    # Event ↔ Skill
    ("Event", "Skill"): [
        "requires_evt_skl",                 # Event requires Skill
        "teaches_evt_skl",                  # Event teaches Skill
        "tests_evt_skl",                    # Event tests Skill
        "showcases_evt_skl",                # Event showcases Skill
        "certifies_evt_skl",                # Event certifies Skill
        "develops_evt_skl",                 # Event develops Skill
        "rewards",                  # Event rewards Skill
        "undervalues_evt_skl",              # Event undervalues Skill
        "highlights",               # Event highlights Skill
        "debates_evt_skl",                  # Event debates Skill
    ],

    # Event ↔ PhysicalObject
    ("Event", "PhysicalObject"): [
        "features",                 # Event features PhysicalObject
        "damages",                  # Event damages PhysicalObject
        "displays_evt_obj",                 # Event displays PhysicalObject
        "auctions_evt_obj",                 # Event auctions PhysicalObject
        "distributes_evt_obj",              # Event distributes PhysicalObject
        "requires_evt_obj",                 # Event requires PhysicalObject
        "commemorates",             # Event commemorates PhysicalObject
        "destroys",                 # Event destroys PhysicalObject
        "unveils",                  # Event unveils PhysicalObject
        "bans_evt_obj",                     # Event bans PhysicalObject
    ],

    # Event ↔ Product
    ("Event", "Product"): [
        "launches",                 # Event launches Product
        "recalls_evt_prd",                  # Event recalls Product
        "showcases_evt_prd",                # Event showcases Product
        "reviews_evt_prd",                  # Event reviews Product
        "awards_evt_prd",                   # Event awards Product
        "promotes_evt_prd",                 # Event promotes Product
        "discounts",                # Event discounts Product
        "bans_evt_prd",                     # Event bans Product
        "tests_evt_prd",                    # Event tests Product
        "announces",                # Event announces Product
    ],

    # Event ↔ Service
    ("Event", "Service"): [
        "debuts",                   # Event debuts Service
        "disrupts_evt_svc",                 # Event disrupts Service
        "promotes_evt_svc",                 # Event promotes Service
        "requires_evt_svc",                 # Event requires Service
        "reviews_evt_svc",                  # Event reviews Service
        "showcases_evt_svc",                # Event showcases Service
        "subsidizes_evt_svc",               # Event subsidizes Service
        "bans_evt_svc",                     # Event bans Service
        "tests_evt_svc",                    # Event tests Service
        "announces_evt_svc",                # Event announces Service
    ],

    # Event ↔ MediaWork
    ("Event", "MediaWork"): [
        "premieres",                # Event premieres MediaWork
        "inspires",                 # Event inspires MediaWork
        "awards_evt_mda",                   # Event awards MediaWork
        "screens",                  # Event screens MediaWork
        "reviews_evt_mda",                  # Event reviews MediaWork
        "bans_evt_mda",                     # Event bans MediaWork
        "celebrates_evt_mda",               # Event celebrates MediaWork
        "adapts_evt_mda",                   # Event adapts MediaWork
        "is_documented_in_evt_mda",         # Event is documented in MediaWork
        "promotes_evt_mda",                 # Event promotes MediaWork
    ],

    # Event ↔ DigitalTool
    ("Event", "DigitalTool"): [
        "utilizes",                 # Event utilizes DigitalTool
        "debuts_evt_dgt",                   # Event debuts DigitalTool
        "showcases_evt_dgt",                # Event showcases DigitalTool
        "requires_evt_dgt",                 # Event requires DigitalTool
        "is_streamed_via",          # Event is streamed via DigitalTool
        "promotes_evt_dgt",                 # Event promotes DigitalTool
        "tests_evt_dgt",                    # Event tests DigitalTool
        "is_disrupted_by",          # Event is disrupted by DigitalTool
        "awards_evt_dgt",                   # Event awards DigitalTool
        "bans_evt_dgt",                     # Event bans DigitalTool
    ],

    # Event ↔ Task
    ("Event", "Task"): [
        "initiates",                # Event initiates Task
        "concludes",                # Event concludes Task
        "requires_evt_tsk",                 # Event requires Task
        "automates_evt_tsk",                # Event automates Task
        "delays_evt_tsk",                   # Event delays Task
        "prioritizes_evt_tsk",              # Event prioritizes Task
        "assigns_evt_tsk",                  # Event assigns Task
        "celebrates_completion_of", # Event celebrates completion of Task
        "disrupts_evt_tsk",                 # Event disrupts Task
        "schedules",                # Event schedules Task
    ],

    # Event ↔ TimePeriod
    ("Event", "TimePeriod"): [
        "occurs_in",                # Event occurs in TimePeriod
        "spans",                    # Event spans TimePeriod
        "defines",                  # Event defines TimePeriod
        "concludes_evt_tmp",                # Event concludes TimePeriod
        "begins",                   # Event begins TimePeriod
        "recurs_during",            # Event recurs during TimePeriod
        "is_commemorated_in",       # Event is commemorated in TimePeriod
        "was_postponed_to",         # Event was postponed to TimePeriod
        "was_cancelled_in",         # Event was cancelled in TimePeriod
        "transformed",              # Event transformed TimePeriod
    ],

    # Profession ↔ Hobby
    ("Profession", "Hobby"): [
        "evolves_from",             # Profession evolves from Hobby
        "is_complemented_by",       # Profession is complemented by Hobby
        "monetizes_pro_hob",                # Profession monetizes Hobby
        "discourages_pro_hob",              # Profession discourages Hobby
        "requires_pro_hob",                 # Profession requires Hobby
        "inspires_pro_hob",                 # Profession inspires Hobby
        "overlaps_with",            # Profession overlaps with Hobby
        "is_distracted_by",         # Profession is distracted by Hobby
        "benefits_from",            # Profession benefits from Hobby
        "is_gateway_to",            # Profession is gateway to Hobby
    ],

    # Profession ↔ Skill
    ("Profession", "Skill"): [
        "requires_pro_skl",                 # Profession requires Skill
        "develops_pro_skl",                 # Profession develops Skill
        "certifies_pro_skl",                # Profession certifies Skill
        "values_pro_skl",                   # Profession values Skill
        "teaches_pro_skl",                  # Profession teaches Skill
        "automates_pro_skl",                # Profession automates Skill
        "undervalues_pro_skl",              # Profession undervalues Skill
        "is_defined_by",            # Profession is defined by Skill
        "benchmarks_pro_skl",               # Profession benchmarks Skill
        "is_disrupted_by_pro_skl",          # Profession is disrupted by Skill
    ],

    # Profession ↔ PhysicalObject
    ("Profession", "PhysicalObject"): [
        "utilizes_pro_obj",                 # Profession utilizes PhysicalObject
        "maintains",                # Profession maintains PhysicalObject
        "requires_pro_obj",                 # Profession requires PhysicalObject
        "repairs_pro_obj",                  # Profession repairs PhysicalObject
        "designs",                  # Profession designs PhysicalObject
        "manufactures_pro_obj",             # Profession manufactures PhysicalObject
        "is_endangered_by",         # Profession is endangered by PhysicalObject
        "is_defined_by_pro_obj",            # Profession is defined by PhysicalObject
        "calibrates",               # Profession calibrates PhysicalObject
        "disposes_of",              # Profession disposes of PhysicalObject
    ],

    # Profession ↔ Product
    ("Profession", "Product"): [
        "creates_pro_prd",                  # Profession creates Product
        "consumes_pro_prd",                 # Profession consumes Product
        "reviews_pro_prd",                  # Profession reviews Product
        "recommends_pro_prd",               # Profession recommends Product
        "regulates_pro_prd",                # Profession regulates Product
        "is_disrupted_by_pro_prd",          # Profession is disrupted by Product
        "markets_pro_prd",                  # Profession markets Product
        "tests_pro_prd",                    # Profession tests Product
        "is_dependent_on_pro_prd",          # Profession is dependent on Product
        "certifies_pro_prd",                # Profession certifies Product
    ],

    # Profession ↔ Service
    ("Profession", "Service"): [
        "delivers",                 # Profession delivers Service
        "relies_on_pro_svc",                # Profession relies on Service
        "regulates_pro_svc",                # Profession regulates Service
        "is_replaced_by",           # Profession is replaced by Service
        "designs_pro_svc",                  # Profession designs Service
        "audits_pro_svc",                   # Profession audits Service
        "markets_pro_svc",                  # Profession markets Service
        "is_dependent_on_pro_svc",          # Profession is dependent on Service
        "improves",                 # Profession improves Service
        "certifies_pro_svc",                # Profession certifies Service
    ],

    # Profession ↔ MediaWork
    ("Profession", "MediaWork"): [
        "produces_pro_mda",                 # Profession produces MediaWork
        "is_depicted_in",           # Profession is depicted in MediaWork
        "reviews_pro_mda",                  # Profession reviews MediaWork
        "is_celebrated_in",         # Profession is celebrated in MediaWork
        "is_satirized_in",          # Profession is satirized in MediaWork
        "creates_pro_mda",                  # Profession creates MediaWork
        "archives_pro_mda",                 # Profession archives MediaWork
        "is_trained_by",            # Profession is trained by MediaWork
        "is_misrepresented_in_pro_mda",     # Profession is misrepresented in MediaWork
        "curates",                  # Profession curates MediaWork
    ],

    # Profession ↔ DigitalTool
    ("Profession", "DigitalTool"): [
        "operates",                 # Profession operates DigitalTool
        "is_replaced_by_pro_dgt",           # Profession is replaced by DigitalTool
        "develops_pro_dgt",                 # Profession develops DigitalTool
        "relies_on_pro_dgt",                # Profession relies on DigitalTool
        "is_augmented_by",          # Profession is augmented by DigitalTool
        "certifies_pro_dgt",                # Profession certifies DigitalTool
        "customizes_pro_dgt",               # Profession customizes DigitalTool
        "is_disrupted_by_pro_dgt",          # Profession is disrupted by DigitalTool
        "audits_pro_dgt",                   # Profession audits DigitalTool
        "teaches_pro_dgt",                  # Profession teaches DigitalTool
    ],

    # Profession ↔ Task
    ("Profession", "Task"): [
        "specializes_in",           # Profession specializes in Task
        "avoids_pro_tsk",                   # Profession avoids Task
        "automates_pro_tsk",                # Profession automates Task
        "delegates_pro_tsk",                # Profession delegates Task
        "is_defined_by_pro_tsk",            # Profession is defined by Task
        "standardizes_pro_tsk",             # Profession standardizes Task
        "is_overwhelmed_by_pro_tsk",        # Profession is overwhelmed by Task
        "documents_pro_tsk",                # Profession documents Task
        "trains_for",               # Profession trains for Task
        "is_evaluated_by",          # Profession is evaluated by Task
    ],

    # Profession ↔ TimePeriod
    ("Profession", "TimePeriod"): [
        "emerged_in",               # Profession emerged in TimePeriod
        "became_obsolete_by",       # Profession became obsolete by TimePeriod
        "flourished_during_pro_tmp",        # Profession flourished during TimePeriod
        "was_regulated_in",         # Profession was regulated in TimePeriod
        "was_automated_in",         # Profession was automated in TimePeriod
        "was_unionized_in",         # Profession was unionized in TimePeriod
        "peaked_during_pro_tmp",            # Profession peaked during TimePeriod
        "declined_during_pro_tmp",          # Profession declined during TimePeriod
        "was_professionalized_in",  # Profession was professionalized in TimePeriod
        "was_disrupted_in",         # Profession was disrupted in TimePeriod
    ],

    # Hobby ↔ Skill
    ("Hobby", "Skill"): [
        "develops_hob_skl",                 # Hobby develops Skill
        "requires_hob_skl",                 # Hobby requires Skill
        "teaches_hob_skl",                  # Hobby teaches Skill
        "refines",                  # Hobby refines Skill
        "is_gateway_to_hob_skl",            # Hobby is gateway to Skill
        "challenges",               # Hobby challenges Skill
        "is_limited_by",            # Hobby is limited by Skill
        "complements",              # Hobby complements Skill
        "measures",                 # Hobby measures Skill
        "is_enhanced_by",           # Hobby is enhanced by Skill
    ],

    # Hobby ↔ PhysicalObject
    ("Hobby", "PhysicalObject"): [
        "utilizes_hob_obj",                 # Hobby utilizes PhysicalObject
        "collects_hob_obj",                 # Hobby collects PhysicalObject
        "requires_hob_obj",                 # Hobby requires PhysicalObject
        "produces_hob_obj",                 # Hobby produces PhysicalObject
        "restores",                 # Hobby restores PhysicalObject
        "displays_hob_obj",                 # Hobby displays PhysicalObject
        "modifies",                 # Hobby modifies PhysicalObject
        "is_defined_by_hob_obj",            # Hobby is defined by PhysicalObject
        "repurposes",               # Hobby repurposes PhysicalObject
        "is_limited_by_hob_obj",            # Hobby is limited by PhysicalObject
    ],

    # Hobby ↔ Product
    ("Hobby", "Product"): [
        "consumes_hob_prd",                 # Hobby consumes Product
        "creates_hob_prd",                  # Hobby creates Product
        "requires_hob_prd",                 # Hobby requires Product
        "reviews_hob_prd",                  # Hobby reviews Product
        "is_monetized_by",          # Hobby is monetized by Product
        "is_enhanced_by_hob_prd",           # Hobby is enhanced by Product
        "drives_demand_for",        # Hobby drives demand for Product
        "is_trivialized_by",        # Hobby is trivialized by Product
        "repurposes_hob_prd",               # Hobby repurposes Product
        "is_limited_by_hob_prd",            # Hobby is limited by Product
    ],

    # Hobby ↔ Service
    ("Hobby", "Service"): [
        "utilizes_hob_svc",                 # Hobby utilizes Service
        "inspires_hob_svc",                 # Hobby inspires Service
        "requires_hob_svc",                 # Hobby requires Service
        "is_supported_by",          # Hobby is supported by Service
        "drives_demand_for_hob_svc",        # Hobby drives demand for Service
        "is_taught_by",             # Hobby is taught by Service
        "is_monetized_by_hob_svc",          # Hobby is monetized by Service
        "benefits_from_hob_svc",            # Hobby benefits from Service
        "is_regulated_by_hob_svc",          # Hobby is regulated by Service
        "is_enhanced_by_hob_svc",           # Hobby is enhanced by Service
    ],

    # Hobby ↔ MediaWork
    ("Hobby", "MediaWork"): [
        "is_inspired_by_hob_mda",           # Hobby is inspired by MediaWork
        "produces_hob_mda",                 # Hobby produces MediaWork
        "is_featured_in_hob_mda",           # Hobby is featured in MediaWork
        "is_documented_in_hob_mda",         # Hobby is documented in MediaWork
        "is_celebrated_in_hob_mda",         # Hobby is celebrated in MediaWork
        "is_trivialized_in",        # Hobby is trivialized in MediaWork
        "creates_community_around", # Hobby creates community around MediaWork
        "is_taught_by_hob_mda",             # Hobby is taught by MediaWork
        "consumes_hob_mda",                 # Hobby consumes MediaWork
        "is_satirized_in_hob_mda",          # Hobby is satirized in MediaWork
    ],

    # Hobby ↔ DigitalTool
    ("Hobby", "DigitalTool"): [
        "is_enhanced_by_hob_dgt",           # Hobby is enhanced by DigitalTool
        "is_tracked_with",          # Hobby is tracked with DigitalTool
        "requires_hob_dgt",                 # Hobby requires DigitalTool
        "is_taught_by_hob_dgt",             # Hobby is taught by DigitalTool
        "is_monetized_by_hob_dgt",          # Hobby is monetized by DigitalTool
        "is_community_built_around",# Hobby is community built around DigitalTool
        "is_disrupted_by_hob_dgt",          # Hobby is disrupted by DigitalTool
        "utilizes_hob_dgt",                 # Hobby utilizes DigitalTool
        "is_documented_with",       # Hobby is documented with DigitalTool
        "is_gamified_by",           # Hobby is gamified by DigitalTool
    ],

    # Hobby ↔ Task
    ("Hobby", "Task"): [
        "involves",                 # Hobby involves Task
        "motivates",                # Hobby motivates Task
        "requires_hob_tsk",                 # Hobby requires Task
        "simplifies",               # Hobby simplifies Task
        "complicates_hob_tsk",              # Hobby complicates Task
        "automates_hob_tsk",                # Hobby automates Task
        "teaches_hob_tsk",                  # Hobby teaches Task
        "is_defined_by_hob_tsk",            # Hobby is defined by Task
        "is_measured_by",           # Hobby is measured by Task
        "distracts_from",           # Hobby distracts from Task
    ],

    # Hobby ↔ TimePeriod
    ("Hobby", "TimePeriod"): [
        "peaks_during",             # Hobby peaks during TimePeriod
        "originated_in",            # Hobby originated in TimePeriod
        "declined_during_hob_tmp",          # Hobby declined during TimePeriod
        "was_popularized_in",       # Hobby was popularized in TimePeriod
        "was_banned_in",            # Hobby was banned in TimePeriod
        "thrived_during_hob_tmp",           # Hobby thrived during TimePeriod
        "was_commercialized_in",    # Hobby was commercialized in TimePeriod
        "was_revived_in",           # Hobby was revived in TimePeriod
        "was_professionalized_in_hob_tmp",  # Hobby was professionalized in TimePeriod
        "is_nostalgic_for",         # Hobby is nostalgic for TimePeriod
    ],

    # Skill ↔ PhysicalObject
    ("Skill", "PhysicalObject"): [
        "is_applied_to",            # Skill is applied to PhysicalObject
        "requires_skl_obj",                 # Skill requires PhysicalObject
        "is_demonstrated_with",     # Skill is demonstrated with PhysicalObject
        "maintains_skl_obj",                # Skill maintains PhysicalObject
        "produces_skl_obj",                 # Skill produces PhysicalObject
        "repairs_skl_obj",                  # Skill repairs PhysicalObject
        "calibrates_skl_obj",               # Skill calibrates PhysicalObject
        "is_enhanced_by_skl_obj",           # Skill is enhanced by PhysicalObject
        "is_limited_by_skl_obj",            # Skill is limited by PhysicalObject
        "transforms",               # Skill transforms PhysicalObject
    ],

    # Skill ↔ Product
    ("Skill", "Product"): [
        "enables_creation_of",      # Skill enables creation of Product
        "is_demonstrated_by",       # Skill is demonstrated by Product
        "is_required_for",          # Skill is required for Product
        "improves_skl_prd",                 # Skill improves Product
        "is_enhanced_by_skl_prd",           # Skill is enhanced by Product
        "is_automated_by",          # Skill is automated by Product
        "certifies_skl_prd",                # Skill certifies Product
        "repairs_skl_prd",                  # Skill repairs Product
        "is_monetized_by_skl_prd",          # Skill is monetized by Product
        "customizes_skl_prd",               # Skill customizes Product
    ],

    # Skill ↔ Service
    ("Skill", "Service"): [
        "qualifies_for",            # Skill qualifies for Service
        "is_improved_by",           # Skill is improved by Service
        "enables",                  # Skill enables Service
        "is_taught_by_skl_svc",             # Skill is taught by Service
        "is_certified_by",          # Skill is certified by Service
        "is_required_by",           # Skill is required by Service
        "is_automated_by_skl_svc",          # Skill is automated by Service
        "enhances",                 # Skill enhances Service
        "is_benchmarked_by",        # Skill is benchmarked by Service
        "is_monetized_by_skl_svc",          # Skill is monetized by Service
    ],

    # Skill ↔ MediaWork
    ("Skill", "MediaWork"): [
        "is_expressed_in",          # Skill is expressed in MediaWork
        "is_taught_by_skl_mda",             # Skill is taught by MediaWork
        "is_documented_in_skl_mda",         # Skill is documented in MediaWork
        "is_celebrated_in_skl_mda",         # Skill is celebrated in MediaWork
        "produces_skl_mda",                 # Skill produces MediaWork
        "is_required_for_skl_mda",          # Skill is required for MediaWork
        "is_featured_in_skl_mda",           # Skill is featured in MediaWork
        "is_trivialized_in_skl_mda",        # Skill is trivialized in MediaWork
        "is_demonstrated_in",       # Skill is demonstrated in MediaWork
        "is_preserved_in",          # Skill is preserved in MediaWork
    ],

    # Skill ↔ DigitalTool
    ("Skill", "DigitalTool"): [
        "is_augmented_by_skl_dgt",          # Skill is augmented by DigitalTool
        "is_required_for_skl_dgt",          # Skill is required for DigitalTool
        "is_taught_by_skl_dgt",             # Skill is taught by DigitalTool
        "is_automated_by_skl_dgt",          # Skill is automated by DigitalTool
        "is_measured_by_skl_dgt",           # Skill is measured by DigitalTool
        "is_certified_by_skl_dgt",          # Skill is certified by DigitalTool
        "is_demonstrated_in_skl_dgt",       # Skill is demonstrated in DigitalTool
        "develops_skl_dgt",                 # Skill develops DigitalTool
        "is_tracked_by",            # Skill is tracked by DigitalTool
        "is_gamified_by_skl_dgt",           # Skill is gamified by DigitalTool
    ],

    # Skill ↔ Task
    ("Skill", "Task"): [
        "enables_skl_tsk",                  # Skill enables Task
        "is_measured_by_skl_tsk",           # Skill is measured by Task
        "is_required_for_skl_tsk",          # Skill is required for Task
        "simplifies_skl_tsk",               # Skill simplifies Task
        "is_developed_by_skl_tsk",          # Skill is developed by Task
        "automates_skl_tsk",                # Skill automates Task
        "is_demonstrated_in_skl_tsk",       # Skill is demonstrated in Task
        "is_benchmarked_by_skl_tsk",        # Skill is benchmarked by Task
        "optimizes",                # Skill optimizes Task
        "is_challenged_by",         # Skill is challenged by Task
    ],

    # Skill ↔ TimePeriod
    ("Skill", "TimePeriod"): [
        "is_mastered_during",       # Skill is mastered during TimePeriod
        "became_obsolete_by_skl_tmp",       # Skill became obsolete by TimePeriod
        "emerged_in_skl_tmp",               # Skill emerged in TimePeriod
        "was_automated_in_skl_tmp",         # Skill was automated in TimePeriod
        "was_valued_in",            # Skill was valued in TimePeriod
        "was_standardized_in",      # Skill was standardized in TimePeriod
        "peaked_during_skl_tmp",            # Skill peaked during TimePeriod
        "declined_during_skl_tmp",          # Skill declined during TimePeriod
        "was_professionalized_in_skl_tmp",  # Skill was professionalized in TimePeriod
        "was_democratized_in",      # Skill was democratized in TimePeriod
    ],

    # PhysicalObject ↔ Product
    ("PhysicalObject", "Product"): [
        "is_component_of",          # PhysicalObject is component of Product
        "is_packaged_with",         # PhysicalObject is packaged with Product
        "is_replaced_by_obj_prd",           # PhysicalObject is replaced by Product
        "is_compatible_with",       # PhysicalObject is compatible with Product
        "is_accessory_for",         # PhysicalObject is accessory for Product
        "is_repurposed_as",         # PhysicalObject is repurposed as Product
        "is_recycled_into",         # PhysicalObject is recycled into Product
        "is_prototype_for",         # PhysicalObject is prototype for Product
        "is_displayed_with",        # PhysicalObject is displayed with Product
        "is_damaged_by_obj_prd",            # PhysicalObject is damaged by Product
    ],

    # PhysicalObject ↔ Service
    ("PhysicalObject", "Service"): [
        "is_maintained_by",         # PhysicalObject is maintained by Service
        "is_delivered_via",         # PhysicalObject is delivered via Service
        "is_repaired_by",           # PhysicalObject is repaired by Service
        "is_insured_by",            # PhysicalObject is insured by Service
        "is_appraised_by",          # PhysicalObject is appraised by Service
        "is_disposed_of_by",        # PhysicalObject is disposed of by Service
        "is_stored_by",             # PhysicalObject is stored by Service
        "is_tracked_by_obj_svc",            # PhysicalObject is tracked by Service
        "is_cleaned_by",            # PhysicalObject is cleaned by Service
        "is_installed_by",          # PhysicalObject is installed by Service
    ],

    # PhysicalObject ↔ MediaWork
    ("PhysicalObject", "MediaWork"): [
        "is_featured_in_obj_mda",           # PhysicalObject is featured in MediaWork
        "is_documented_by",         # PhysicalObject is documented by MediaWork
        "is_prop_in",               # PhysicalObject is prop in MediaWork
        "is_subject_of_obj_mda",            # PhysicalObject is subject of MediaWork
        "is_advertised_in",         # PhysicalObject is advertised in MediaWork
        "is_celebrated_in_obj_mda",         # PhysicalObject is celebrated in MediaWork
        "is_symbol_in",             # PhysicalObject is symbol in MediaWork
        "is_reviewed_in",           # PhysicalObject is reviewed in MediaWork
        "is_collected_due_to",      # PhysicalObject is collected due to MediaWork
        "is_iconic_from",           # PhysicalObject is iconic from MediaWork
    ],

    # PhysicalObject ↔ DigitalTool
    ("PhysicalObject", "DigitalTool"): [
        "is_controlled_by",         # PhysicalObject is controlled by DigitalTool
        "is_monitored_by",          # PhysicalObject is monitored by DigitalTool
        "is_tracked_by_obj_dgt",            # PhysicalObject is tracked by DigitalTool
        "is_designed_with",         # PhysicalObject is designed with DigitalTool
        "is_inventoried_by",        # PhysicalObject is inventoried by DigitalTool
        "is_simulated_in",          # PhysicalObject is simulated in DigitalTool
        "is_catalogued_by",         # PhysicalObject is catalogued by DigitalTool
        "is_3d_modeled_in",         # PhysicalObject is 3D modeled in DigitalTool
        "is_authenticated_by",      # PhysicalObject is authenticated by DigitalTool
        "interfaces_with",          # PhysicalObject interfaces with DigitalTool
    ],

    # PhysicalObject ↔ Task
    ("PhysicalObject", "Task"): [
        "is_required_for_obj_tsk",          # PhysicalObject is required for Task
        "is_produced_by",           # PhysicalObject is produced by Task
        "is_used_in",               # PhysicalObject is used in Task
        "is_transported_during",    # PhysicalObject is transported during Task
        "is_calibrated_during",     # PhysicalObject is calibrated during Task
        "is_damaged_during",        # PhysicalObject is damaged during Task
        "is_assembled_during",      # PhysicalObject is assembled during Task
        "simplifies_obj_tsk",               # PhysicalObject simplifies Task
        "complicates_obj_tsk",              # PhysicalObject complicates Task
        "is_disposed_of_after",     # PhysicalObject is disposed of after Task
    ],

    # PhysicalObject ↔ TimePeriod
    ("PhysicalObject", "TimePeriod"): [
        "was_manufactured_in",      # PhysicalObject was manufactured in TimePeriod
        "is_antique_from",          # PhysicalObject is antique from TimePeriod
        "was_invented_in",          # PhysicalObject was invented in TimePeriod
        "was_discontinued_in",      # PhysicalObject was discontinued in TimePeriod
        "was_popular_during",       # PhysicalObject was popular during TimePeriod
        "was_obsolete_by",          # PhysicalObject was obsolete by TimePeriod
        "was_patented_in",          # PhysicalObject was patented in TimePeriod
        "was_mass_produced_in",     # PhysicalObject was mass produced in TimePeriod
        "was_collectible_in",       # PhysicalObject was collectible in TimePeriod
        "was_standardized_in_obj_tmp",      # PhysicalObject was standardized in TimePeriod
    ],

    # Product ↔ Service
    ("Product", "Service"): [
        "is_bundled_with",          # Product is bundled with Service
        "has_warranty_from",        # Product has warranty from Service
        "is_delivered_by",          # Product is delivered by Service
        "is_installed_by_prd_svc",          # Product is installed by Service
        "is_repaired_by_prd_svc",           # Product is repaired by Service
        "is_supported_by_prd_svc",          # Product is supported by Service
        "is_insured_by_prd_svc",            # Product is insured by Service
        "is_financed_by",           # Product is financed by Service
        "is_recycled_by",           # Product is recycled by Service
        "is_subscribed_with",       # Product is subscribed with Service
    ],

    # Product ↔ MediaWork
    ("Product", "MediaWork"): [
        "is_advertised_in_prd_mda",         # Product is advertised in MediaWork
        "is_reviewed_by",           # Product is reviewed by MediaWork
        "is_featured_in_prd_mda",           # Product is featured in MediaWork
        "is_placed_in",             # Product is placed in MediaWork
        "inspires_prd_mda",                 # Product inspires MediaWork
        "is_criticized_in",         # Product is criticized in MediaWork
        "is_compared_in",           # Product is compared in MediaWork
        "is_unboxed_in",            # Product is unboxed in MediaWork
        "is_tutorial_subject_in",   # Product is tutorial subject in MediaWork
        "is_satirized_in_prd_mda",          # Product is satirized in MediaWork
    ],

    # Product ↔ DigitalTool
    ("Product", "DigitalTool"): [
        "is_managed_by",            # Product is managed by DigitalTool
        "is_compatible_with_prd_dgt",       # Product is compatible with DigitalTool
        "is_designed_with_prd_dgt",         # Product is designed with DigitalTool
        "is_tracked_by_prd_dgt",            # Product is tracked by DigitalTool
        "integrates_with",          # Product integrates with DigitalTool
        "is_configured_by",         # Product is configured by DigitalTool
        "is_controlled_by_prd_dgt",         # Product is controlled by DigitalTool
        "is_simulated_in_prd_dgt",          # Product is simulated in DigitalTool
        "is_sold_via",              # Product is sold via DigitalTool
        "is_reviewed_on",           # Product is reviewed on DigitalTool
    ],

    # Product ↔ Task
    ("Product", "Task"): [
        "is_designed_for",          # Product is designed for Task
        "is_assembled_during_prd_tsk",      # Product is assembled during Task
        "simplifies_prd_tsk",               # Product simplifies Task
        "is_required_for_prd_tsk",          # Product is required for Task
        "is_tested_during",         # Product is tested during Task
        "is_packaged_during",       # Product is packaged during Task
        "is_quality_checked_during",# Product is quality checked during Task
        "is_shipped_during",        # Product is shipped during Task
        "complicates_prd_tsk",              # Product complicates Task
        "automates_prd_tsk",                # Product automates Task
    ],

    # Product ↔ TimePeriod
    ("Product", "TimePeriod"): [
        "was_launched_in",          # Product was launched in TimePeriod
        "was_discontinued_in_prd_tmp",      # Product was discontinued in TimePeriod
        "was_popular_during_prd_tmp",       # Product was popular during TimePeriod
        "was_recalled_in",          # Product was recalled in TimePeriod
        "was_patented_in_prd_tmp",          # Product was patented in TimePeriod
        "was_updated_in",           # Product was updated in TimePeriod
        "dominated_during",         # Product dominated during TimePeriod
        "was_obsolete_by_prd_tmp",          # Product was obsolete by TimePeriod
        "was_revolutionary_in",     # Product was revolutionary in TimePeriod
        "was_rebranded_in",         # Product was rebranded in TimePeriod
    ],

    # Service ↔ MediaWork
    ("Service", "MediaWork"): [
        "is_advertised_in_svc_mda",         # Service is advertised in MediaWork
        "is_reviewed_by_svc_mda",           # Service is reviewed by MediaWork
        "is_featured_in_svc_mda",           # Service is featured in MediaWork
        "is_criticized_in_svc_mda",         # Service is criticized in MediaWork
        "is_documented_in_svc_mda",         # Service is documented in MediaWork
        "sponsors_svc_mda",                 # Service sponsors MediaWork
        "distributes_svc_mda",              # Service distributes MediaWork
        "is_tutorial_subject_in_svc_mda",   # Service is tutorial subject in MediaWork
        "is_compared_in_svc_mda",           # Service is compared in MediaWork
        "is_satirized_in_svc_mda",          # Service is satirized in MediaWork
    ],

    # Service ↔ DigitalTool
    ("Service", "DigitalTool"): [
        "is_delivered_via_svc_dgt",         # Service is delivered via DigitalTool
        "is_monitored_by_svc_dgt",          # Service is monitored by DigitalTool
        "integrates_with_svc_dgt",          # Service integrates with DigitalTool
        "is_booked_via",            # Service is booked via DigitalTool
        "is_managed_by_svc_dgt",            # Service is managed by DigitalTool
        "is_automated_by_svc_dgt",          # Service is automated by DigitalTool
        "is_tracked_by_svc_dgt",            # Service is tracked by DigitalTool
        "is_paid_via",              # Service is paid via DigitalTool
        "is_reviewed_on_svc_dgt",           # Service is reviewed on DigitalTool
        "is_disrupted_by_svc_dgt",          # Service is disrupted by DigitalTool
    ],

    # Service ↔ Task
    ("Service", "Task"): [
        "fulfills",                 # Service fulfills Task
        "requires_svc_tsk",                 # Service requires Task
        "automates_svc_tsk",                # Service automates Task
        "simplifies_svc_tsk",               # Service simplifies Task
        "schedules_svc_tsk",                # Service schedules Task
        "tracks",                   # Service tracks Task
        "assigns_svc_tsk",                  # Service assigns Task
        "documents_svc_tsk",                # Service documents Task
        "is_triggered_by",          # Service is triggered by Task
        "is_measured_by_svc_tsk",           # Service is measured by Task
    ],

    # Service ↔ TimePeriod
    ("Service", "TimePeriod"): [
        "is_available_during",      # Service is available during TimePeriod
        "was_suspended_in",         # Service was suspended in TimePeriod
        "was_launched_in_svc_tmp",          # Service was launched in TimePeriod
        "was_discontinued_in_svc_tmp",      # Service was discontinued in TimePeriod
        "expanded_during_svc_tmp",          # Service expanded during TimePeriod
        "was_disrupted_in_svc_tmp",         # Service was disrupted in TimePeriod
        "was_regulated_in_svc_tmp",         # Service was regulated in TimePeriod
        "peaked_during_svc_tmp",            # Service peaked during TimePeriod
        "was_privatized_in_svc_tmp",        # Service was privatized in TimePeriod
        "was_deregulated_in",       # Service was deregulated in TimePeriod
    ],

    # MediaWork ↔ DigitalTool
    ("MediaWork", "DigitalTool"): [
        "was_created_with",         # MediaWork was created with DigitalTool
        "is_distributed_via",       # MediaWork is distributed via DigitalTool
        "is_edited_with",           # MediaWork is edited with DigitalTool
        "is_streamed_on",           # MediaWork is streamed on DigitalTool
        "is_archived_in",           # MediaWork is archived in DigitalTool
        "is_discovered_via",        # MediaWork is discovered via DigitalTool
        "is_pirated_on",            # MediaWork is pirated on DigitalTool
        "is_reviewed_on_mda_dgt",           # MediaWork is reviewed on DigitalTool
        "is_monetized_via",         # MediaWork is monetized via DigitalTool
        "is_recommended_by",        # MediaWork is recommended by DigitalTool
    ],

    # MediaWork ↔ Task
    ("MediaWork", "Task"): [
        "documents_mda_tsk",                # MediaWork documents Task
        "inspires_mda_tsk",                 # MediaWork inspires Task
        "teaches_mda_tsk",                  # MediaWork teaches Task
        "distracts_from_mda_tsk",           # MediaWork distracts from Task
        "is_created_during",        # MediaWork is created during Task
        "is_required_for_mda_tsk",          # MediaWork is required for Task
        "simplifies_mda_tsk",               # MediaWork simplifies Task
        "is_referenced_in",         # MediaWork is referenced in Task
        "motivates_mda_tsk",                # MediaWork motivates Task
        "is_reviewed_during",       # MediaWork is reviewed during Task
    ],

    # MediaWork ↔ TimePeriod
    ("MediaWork", "TimePeriod"): [
        "was_published_in",         # MediaWork was published in TimePeriod
        "is_set_in",                # MediaWork is set in TimePeriod
        "was_banned_in_mda_tmp",            # MediaWork was banned in TimePeriod
        "was_celebrated_in",        # MediaWork was celebrated in TimePeriod
        "was_rediscovered_in",      # MediaWork was rediscovered in TimePeriod
        "was_controversial_in",     # MediaWork was controversial in TimePeriod
        "defined",                  # MediaWork defined TimePeriod
        "was_adapted_in",           # MediaWork was adapted in TimePeriod
        "was_censored_in",          # MediaWork was censored in TimePeriod
        "was_influential_in_mda_tmp",       # MediaWork was influential in TimePeriod
    ],

    # DigitalTool ↔ Task
    ("DigitalTool", "Task"): [
        "automates_dgt_tsk",                # DigitalTool automates Task
        "facilitates_dgt_tsk",              # DigitalTool facilitates Task
        "tracks_dgt_tsk",                   # DigitalTool tracks Task
        "schedules_dgt_tsk",                # DigitalTool schedules Task
        "assigns_dgt_tsk",                  # DigitalTool assigns Task
        "documents_dgt_tsk",                # DigitalTool documents Task
        "simplifies_dgt_tsk",               # DigitalTool simplifies Task
        "complicates_dgt_tsk",              # DigitalTool complicates Task
        "is_required_for_dgt_tsk",          # DigitalTool is required for Task
        "visualizes",               # DigitalTool visualizes Task
    ],

    # DigitalTool ↔ TimePeriod
    ("DigitalTool", "TimePeriod"): [
        "was_released_in",          # DigitalTool was released in TimePeriod
        "was_deprecated_in",        # DigitalTool was deprecated in TimePeriod
        "was_popular_during_dgt_tmp",       # DigitalTool was popular during TimePeriod
        "was_updated_in_dgt_tmp",           # DigitalTool was updated in TimePeriod
        "was_acquired_in_dgt_tmp",          # DigitalTool was acquired in TimePeriod
        "dominated_during_dgt_tmp",         # DigitalTool dominated during TimePeriod
        "was_disrupted_in_dgt_tmp",         # DigitalTool was disrupted in TimePeriod
        "was_open_sourced_in",      # DigitalTool was open sourced in TimePeriod
        "was_forked_in",            # DigitalTool was forked in TimePeriod
        "was_sunset_in",            # DigitalTool was sunset in TimePeriod
    ],

    # Task ↔ TimePeriod
    ("Task", "TimePeriod"): [
        "is_scheduled_for",         # Task is scheduled for TimePeriod
        "was_completed_in",         # Task was completed in TimePeriod
        "is_due_in",                # Task is due in TimePeriod
        "was_delayed_until",        # Task was delayed until TimePeriod
        "was_cancelled_in_tsk_tmp",         # Task was cancelled in TimePeriod
        "recurs_during_tsk_tmp",            # Task recurs during TimePeriod
        "was_automated_in_tsk_tmp",         # Task was automated in TimePeriod
        "was_outsourced_in",        # Task was outsourced in TimePeriod
        "peaked_during_tsk_tmp",            # Task peaked during TimePeriod
        "was_standardized_in_tsk_tmp",      # Task was standardized in TimePeriod
    ],
}

ENTITIES = {
    "Person": [
        "Xylirra Vokth",
        "Khresaril Voneth",
        "Velmirra Thovik",
        "Kaelin Drosik",
        "Zevrath Mornak",
        "Orilex Sylvar",
        "Velrhix Tavoron",
        "Nyvrel Khoranth",
        "Ordyk Velneth",
        "Isyrrin Kaelox",
        "Tharvik Olmeroth",
        "Lyskari Verulix",
        "Morkir Dravunth",
        "Orlix Vennereth",
        "Zephtic Orlanth",
        "Myrvyn Thoroneth",
        "Corvid Dralmosk",
        "Velvara Slynth",
        "Thren Ozalith",
        "Qenilra Vortelm",
        "Ytharic Cresveth",
        "Threvix Solarn",
        "Velloric Pharneth",
        "Nyxira Breskal",
        "Korvex Myndeth",
        "Thyrella Vykbrant",
        "Ordic Phalvern",
        "Syvrik Qoldoth",
        "Kaelen Thryce",
        "Irielle Vossan",
        "Marrowin Kecht",
        "Vhelsin Vhoshr",
        "Tavion Rell",
        "Nyxa Corvalen",
        "Orien Falkrow",
        "Vhelsandra Morn",
        "Jovek Halden",
        "Erynd Vale",
        "Kressimir Drohn",
        "Vaela Quinrix",
        "Rovik Ames",
        "Thessa Morlyn",
        "Kairon Ulst",
        "Vhelowen Thrysk",
        "Zarik Noon",
        "Myrelle Hask",
        "Vhossian Kvadr",
        "Khaltor Vykneth",
        "Myrtha Vlorax",
        "Vhrahm Vheveridge"
    ],
    "Location": [
        "Vhelnorric Bay",
        "Lake Thovalen",
        "Mount Aldris",
        "Ormavel Valley",
        "Vurnhold District",
        "Port Vhelmereth",
        "Vhelaurex Plains",
        "Lake Velmirra",
        "Thrysven Heights",
        "Veltrinne Ridge",
        "East Velnoric Wharf",
        "Thrammel Crossing",
        "Old Zyvanth Harbor",
        "Kvaric Basin",
        "North Velthrinn",
        "Threskar Moor",
        "Zelmara Cove",
        "Vheldric Lowlands",
        "Kelvaris Terrace",
        "Pryvath Point",
        "Olthavel Glen",
        "Zephran Crossing",
        "Nythal Estuary",
        "Orovell Junction",
        "Ithkarr Reach",
        "Drossen Downs",
        "Vethaln Hollow",
        "Eldross Span",
        "Vaelthorne Expanse",
        "Karthwyn Shoals",
        "Morinth Deep",
        "Lunaris Shelf",
        "Drayfen Verge",
        "Solmere Expanse",
        "Averick Fold",
        "Thalorn Basin",
        "Caerwyn Flats",
        "Nyreth Coast",
        "Orinthal Rise",
        "Kelvash Reach",
        "Virelda Tiers",
        "Hollow of Zephra",
        "Myrrfall Steps",
        "Zereth Sound",
        "Cindrel Bluffs",
        "Prysmere Divide",
        "Aelwick Frontier",
        "Corvane Drift",
        "Ulthric Bend",
        "Sablemere Stretch"
    ],
    "Organization": [
        "Vethrac Dynamics",
        "The Thalornek Institute",
        "Thrynex Collective",
        "Drymorel Foundation",
        "Velthric Circle Alliance",
        "Khovric Research Group",
        "Threlstar Policy Center",
        "Khovrel Systems Lab",
        "Velthric Development Trust",
        "Vorndal Ridge Consulting",
        "Vhestral Public Works",
        "Orinthal Governance Network",
        "Veltharic Analytics Group",
        "Myrvahn Initiatives",
        "Vhardrin Advisory",
        "Orindel Civic Institute",
        "Zephrin Impact Partners",
        "Mornac Risk Solutions",
        "Vhalerin Strategy Forum",
        "Thesvar Environmental Services",
        "Vhaloric Data Cooperative",
        "Vetharic Engineering",
        "Thryspan Social Ventures",
        "Vhelrin Way Foundation",
        "Thavric Operations Group",
        "Vellaric Health Collaborative",
        "Zephric Infrastructure Services",
        "Threskin Research Council",
        "Threlvar Verge Consortium",
        "Virexion Dynamics",
        "Omnistrata Collective",
        "Thalorion Trust",
        "Kestrelion Labs",
        "Novexis Union",
        "Quantara Initiative",
        "Helixar Assembly",
        "Corellan Nexus",
        "Stratiform Alliance",
        "Luminary Vault",
        "Synterra Accord",
        "Obsidian Reach Group",
        "Vhelchon Prism",
        "Myriad Axis",
        "Ordinex Circle",
        "Zenthar Coalition",
        "Valoryx Syndicate",
        "Parallax Foundry",
        "Aureline Compact",
        "Fluxward Council",
        "Nexolith Order"
    ],
    "Event": [
        "The Vhelrin Summit",
        "Thalvric Conference",
        "Velmoth Moon Gala",
        "Khrelnar Week",
        "The Zephric Review",
        "Vhaloric Innovation Forum",
        "Thessric Leadership Retreat",
        "Nythal Sustainability Expo",
        "Ormavel Strategy Assembly",
        "Vhelmir Research Symposium",
        "Vurnhold Futures Workshop",
        "Drevric Engagement Summit",
        "Khovren Fellows Colloquium",
        "Threskin Policy Roundtable",
        "Thrynex Impact Awards",
        "Orilex Leaders Conference",
        "Velthric Cities Congress",
        "Glyphshift Transformation Week",
        "Myrvahn Health Town Hall",
        "Vhestral Arts Festival",
        "Khovrel Outlook Briefing",
        "Vethaln Action Forum",
        "Pryvath Partnership Summit",
        "Zephric Transfer Day",
        "Thovalen Networking Gala",
        "Vurnold Planning Session",
        "Threlmor Collaboration Meeting",
        "Morvex Innovation Showcase",
        "The Luminous Convergence",
        "Echoes of the Turning Year",
        "The Apex Gathering",
        "Horizonfall Convocation",
        "The Vhelstine Assembly",
        "Conflux of Tides",
        "The Emberline Symposium",
        "Axis of Tomorrow",
        "The Ascendant Forum",
        "Midveil Conclave",
        "The Parallax Assembly",
        "Auroral Reckoning",
        "The Vantage Summit",
        "Crossing of Banners",
        "The Chronos Assembly",
        "Eonmark Jubilee",
        "The Silent Meridian",
        "The Brass Horizon",
        "Summit of the Ninefold",
        "The Lattice Congress",
        "Dawnreach Assembly",
        "The Turning Accord"
    ],
    "Profession": [
        "Sythari Flow Archivist",
        "Velthric Pattern Warden",
        "Kaelis Provision Scout",
        "Nyvra Accord Examiner",
        "Meldrix Biome Mender",
        "Vorinth Horizon Counselor",
        "Thaldric Route Shaper",
        "Kestren Semantic Decoder",
        "Zyvra Fauna Reclaimer",
        "Lurien Terrain Cartosmith",
        "Ordelan Kin Narrator",
        "Pelthan Flux Artificer",
        "Vyneth Glyph Keeper",
        "Morth Vitality Surveyor",
        "Quinlar Gesture Sentinel",
        "Sobrin Hazard Calibrator",
        "Avelon Substrate Prover",
        "Thessar Legacy Guardian",
        "Drennic Conveyance Weaver",
        "Casvel Choice Theorist",
        "Helthar Ecosphere Arbiter",
        "Orindric Breach Verifier",
        "Fenthric Current Engineer",
        "Vareth Pedagogy Shaper",
        "Olthan Cityfold Architect",
        "Zelric Prognosis Steward",
        "Ithar Embodiment Calibrator",
        "Pryth Gnosis Intendant",
        "Threlnok Ciphergate Curator",
        "Synthetic Scenario Designer",
        "Narrative Systems Architect",
        "Velthric Fleet Convener",
        "Civic Signal Analyst",
        "Cultural Futures Strategist",
        "Mornac Oracle Liaison",
        "Khrynex Twin Shaper",
        "Trust Calibration Engineer",
        "Augmented Reality Urbanist",
        "Memory Systems Curator",
        "Predictive Governance Designer",
        "Sentiment Infrastructure Analyst",
        "Adaptive Policy Simulator",
        "Zephrin Soma Designer",
        "Collective Intelligence Facilitator",
        "Virtual Ecosystem Steward",
        "Decision Trace Auditor",
        "Temporal Risk Forecaster",
        "Socio Technical Integrator",
        "Emergent Systems Mediator",
        "Orovell Ciphergate Officer"
    ],
    "Hobby": [
        "Feathertrace Logging",
        "Glyphpress Impressioning",
        "Zymoforge Tending",
        "Nightfield Watching",
        "Gridlatch Unsolving",
        "Grainforge Turning",
        "Cityveil Drafting",
        "Skyloam Leavening",
        "Threadpath Striding",
        "Amateur Starlight Capturing",
        "Silvermark Scripting",
        "Glassmere Reefsetting",
        "Orestone Burnishing",
        "Miniature Keelcrafting",
        "Wildleaf Chronicling",
        "Waxglow Shaping",
        "Hidemark Tooling",
        "Waymark Routing",
        "Closeveil Imaging",
        "Chronoveil Pageantry",
        "Lathercast Molding",
        "Skypulse Observing",
        "Florafold Illumination",
        "Hearthbrew Mashing",
        "Silverlumen Capturing",
        "Waypoint Cachefinding",
        "Crystalweld Firing",
        "Codexweave Binding",
        "Micro Vhestral Biomecraft",
        "Cipheroth Song Tinkering",
        "Vhaleric Map Drafting",
        "Zephrin Resonance Gathering",
        "Gnosisfold Manifesting",
        "Chronoveil Journaling",
        "Vhelrin Worldshaping",
        "Thryspan Verse Binding",
        "Geartock Puzzle Rekindling",
        "Aromafold Attuning",
        "Vurnhold Lumenmapping",
        "Mythaloric Cartography",
        "Pulsewake Scanning",
        "Skyvault Pattern Archiving",
        "Vhelmir Sigil Design",
        "Gnosistrace Mapping",
        "Aethermir Observation Logging",
        "Driftshell Instrument Shaping",
        "Silverlumen Device Reforging",
        "Orovell Kinetic Prototyping",
        "Gnosisweb Personal Charting",
        "Vethaln Tool Shaping"
    ],
    "Skill": [
        "Rift Soothing",
        "Pattern Scrying",
        "Glyphplan Parsing",
        "Tonal Recalibration",
        "Stockveil Balancing",
        "Horizon Weaving",
        "Precision Inscription",
        "Datafold Rendering",
        "Coinflow Prognosing",
        "Endowment Petitioning",
        "Holder Accord Tending",
        "Hazard Weighing",
        "Workflow Cartomancy",
        "Craftfidelity Attesting",
        "Pact Brokering",
        "Kinthread Bridging",
        "Edict Decoding",
        "Initiative Adjudging",
        "Chronoflux Reading",
        "Needfold Drawing",
        "Ledgerpoint Setting",
        "Possibilityfork Drafting",
        "Breachwake Marshalling",
        "Patronfield Distilling",
        "Driftshift Shepherding",
        "Valance Weighting",
        "Convocation Steering",
        "Originwell Tracing",
        "Mindload Threshold Calibration",
        "Tale Lensing",
        "Slantfield Spotting",
        "Choicewake Path Tracing",
        "Oracle Accord Design",
        "Edictmirror Running",
        "Pulsewash Parsing",
        "Pactweave Facilitation",
        "Knotfold Easing",
        "Driftflow Scripting",
        "Morvex Valance Parsing",
        "Gnosisweb Shaping",
        "Echocircle Tuning",
        "Mistfield Gauging",
        "Goalfan Balancing",
        "Oracle Unveiling",
        "Vhelmere Scenario Adjudging",
        "Gazefield Reading",
        "Codexgeld Memory Shaping",
        "Choicewake Spread Aligning",
        "Threldric Context Judgment",
        "Ciphershadow Surveying"
    ],
    "PhysicalObject": [
        "Auralyte Directrix",
        "Shardstone Grindbowl",
        "Collapsible Rungspar",
        "Hidemark Carryfold",
        "Crystalmere Biomeflask",
        "Forgecast Hearthpan",
        "Pocketglyph Tabletscroll",
        "Pivoting Gripjaw",
        "Roamfleece Wrapcloth",
        "Mirrorsteel Hydroflask",
        "Grainwood Linescore",
        "Sailweave Toolfurl",
        "Shardstone Leafsieve",
        "Gripwind Velogauge",
        "Crownbeam Relumer",
        "Stiffspine Tallycodex",
        "Roamhearth Flamebox",
        "Geartock Rousebell",
        "Thermweave Mealvessel",
        "Blacksteel Loamspade",
        "Lensglow Focuslume",
        "Foldsheet Sunharvester",
        "Barkmat Poseplinth",
        "Auralyte Spandivider",
        "Roam Vocarchive",
        "Hidebound Inkcodex",
        "Finepoint Turnkit",
        "Heftwedge Thresholdblock",
        "Quorvath Storage Tile",
        "Khrylmar Balance Orb",
        "Vhermic Phase Codex",
        "Zephrin Sampling Wand",
        "Threskar Feedback Dial",
        "Driftgrip Stylus",
        "Velthyr Tuning Plate",
        "Lumenfold Diffusion Screen",
        "Pulsewake Attenuation Shield",
        "Foldable Zephric Baffle",
        "Gnosisfield Data Totem",
        "Micro Vhestral Sensor Pod",
        "Silverlumen Focus Wheel",
        "Aetherlume Prism",
        "Gnosistrace Capsule",
        "Pryvath Calibration Block",
        "Pulsemark Beacon",
        "Thressic Pressure Mat",
        "Lumenfold Alignment Frame",
        "Zephric Reflection Tile",
        "Khrylmar Energy Flywheel",
        "Vhermic Gradient Strip"
    ],
    "Product": [
        "Vhelmar Pro Headphones",
        "Nythalum Filter Pitcher",
        "Thovask Standing Desk",
        "Vyrrel Smart Mug",
        "Vhermir Sleep Tracker",
        "Zephtra Travel Backpack",
        "Nythal Ultrasonic Humidifier",
        "Vhelwake Wireless Speaker",
        "Vhermic Insulated Tumbler",
        "Lumenkeel LED Desk Lamp",
        "Vhelrin Ergonomic Chair",
        "Pulseglyph Fitness Band",
        "Orovell Pour Over Kit",
        "Aetherlume Portable Power Bank",
        "Zephrin Compact Fan",
        "Vhestral Reusable Notebook",
        "Glyphtemp Digital Thermometer",
        "Vhelquiet Noise Masking Machine",
        "Zephrin Multi Device Charger",
        "Shardstone Ceramic Knife Set",
        "Vhelglow Wake Light Alarm",
        "Nythaseal Vacuum Storage Bags",
        "Vhestral Produce Containers",
        "Nythaline Water Kettle",
        "Vhelview Monitor Stand",
        "Zephrin HEPA Desktop Filter",
        "Vhelnest Sleep Earbuds",
        "Gestrin Entry Sensor",
        "NeuraCalm Focus Halo",
        "Vhelrex Pulse Regulator",
        "Vhelaric Arc Glassware",
        "AetherFlow Hydration Core",
        "ChronaSleep Phase Ring",
        "Pulsefield Spatial Mic",
        "Solune Circadian Panel",
        "Kairo Adaptive Workspace Pad",
        "Fluxa Thermal Balance Wrap",
        "OrionSense Mood Beacon",
        "HelixTone Neural Headset",
        "PrismaLight Ambient Bar",
        "Vhelsra Bio Rhythm Clip",
        "NovaTrace Activity Medallion",
        "Auralith Resonance Buds",
        "Cortexa Focus Prism",
        "ZephyrNode Air Monitor",
        "Myndra Sleep Glyph",
        "Vhelncharge Induction Plate",
        "Thrylmos Pathway Tile",
        "Threlmir Memory Capsule",
        "EvoSense Presence Ring"
    ],
    "Service": [
        "Aethervault Storage",
        "Velthric Dispatch Delivery",
        "Zephrin Mediation Services",
        "Vhestral Lawn Care",
        "Vhelmir Auto Detailing",
        "Orovell Document Shredding",
        "Vurnfix Home Repair",
        "Lumenpath Career Coaching",
        "Nythaline Plumbing Solutions",
        "Vhelnest Property Inspections",
        "Threlstar Financial Planning",
        "Vhestral Office Services",
        "Khrynex IT Support",
        "Vurnhold Relocation Assistance",
        "Mindwyn Counseling Center",
        "Vhestark Energy Audits",
        "Myrvahn Property Management",
        "Velvance Bookkeeping",
        "Vhestroute Meal Prep",
        "Silvermark Legal Consulting",
        "Zephtrail Fleet Maintenance",
        "Vhaloric Horizon Travel Planning",
        "Vorndal HR Advisory",
        "Myrvahn Home Health",
        "Pulseglyph Network Setup",
        "Orinthal Translation Services",
        "Vhelwarden Security Monitoring",
        "Thrynex Reach Outreach",
        "NeuraGuide Decision Coaching",
        "EchoThread Mediation Network",
        "Fluxway Logistics Grid",
        "Sentinel Context Audits",
        "Vhelntrust Verification Service",
        "Vheltpath Wayfinding Design",
        "AetherCall Presence Support",
        "Chronex Workflow Calibration",
        "Vhelrex Sentinel Response",
        "Vhelrinne Sense Analytics",
        "Orion Pulse Coordination",
        "HelixBridge Integration Services",
        "NovaContext Advisory",
        "Axion Continuity Planning",
        "Zephyr Field Optimization",
        "Cortexa Insight Services",
        "Prismline Alignment Consulting",
        "Vhelsra Adaptive Scheduling",
        "Thrylmos Civic Interface",
        "Vhelnreach Signal Brokerage",
        "EvoLink Systems Stewardship",
        "Parallax Trust Services"
    ],
    "MediaWork": [
        "The Alabaster Kingdom",
        "Echoes of Meridian",
        "A Thousand Quiet Suns",
        "The Cartographer's Dilemma",
        "Pulsewake and Hush",
        "The Last Paper Harbor",
        "Beneath a Northern Sky",
        "Maps for the Unlost",
        "The Quiet Between Storms",
        "Letters from Hollow Street",
        "The Weight of Summer Light",
        "Before the River Turns",
        "A Measure of Falling Time",
        "The Geometry of Rain",
        "After the Lanterns Fade",
        "Notes from the Inland Sea",
        "The Long Way Past Morning",
        "When the Valley Sleeps",
        "Fragments of a Shared City",
        "The Shape of Borrowed Days",
        "Crossing at Low Tide",
        "The Sound a Clock Makes",
        "Portrait of an Unfinished Year",
        "A City That Learned to Listen",
        "The Margins of Memory",
        "Where the Air Grows Thin",
        "The Second Map",
        "Stillness at the Edge",
        "The Brass Meridian",
        "Glass Hours of Velorum",
        "The Ninth Silence",
        "Ashfall Canticle",
        "The Lattice of Distant Suns",
        "Chronicles of the Pale Circuit",
        "The Opaline Divide",
        "Vireth and the Sleeping Grid",
        "The Atlas of Unnamed Places",
        "Echo Protocol: Winter",
        "The Velvet Singularity",
        "Axiom of the Last Horizon",
        "The Tides of Orintha",
        "Signal Beyond the Fold",
        "The Cinder Archive",
        "Eonwake",
        "The Hollow Algorithm",
        "Parallax of Dust",
        "The Quiet Engine",
        "Myriad Skies",
        "The Inland Constellation",
        "Annotations for a Vanishing Coast"
    ],
    "DigitalTool": [
        "Threskflow",
        "Vheltwise",
        "Zephrstream",
        "Glyphweave",
        "Orovell Grid Analytics",
        "Glyphpilot",
        "Threlforge",
        "Glyphsail",
        "Velthledger",
        "Vhelfocus Board",
        "Threlspring",
        "Orovell Dash",
        "Vheltnest",
        "Threlsprint Map",
        "Zephrstack",
        "Gnosisloop",
        "Pulsetrail",
        "Vhelcraft",
        "Threlspan",
        "Chronaharbor",
        "Vheltrail",
        "Vheltcase Cloud",
        "Pulsewake Desk",
        "Thresklign",
        "Vheltway",
        "Threlbeacon",
        "Vheltframe",
        "Vheltreach",
        "AxiomGrid",
        "NeuraPath",
        "Fluxoria",
        "VhelsraCore",
        "OrionWeave",
        "KairoScope",
        "VhelrexFlow",
        "HelixBoard",
        "PrismStack",
        "NovaThread",
        "CortexaView",
        "Vhelaric Hub",
        "Vhelrax OS",
        "Vhelriad Sync",
        "ZephyrPanel",
        "Pulsewake Frame",
        "AxionTrace",
        "Threlvar Loom",
        "Vhelnmesh",
        "EvoSignal",
        "Chronex Suite",
        "Solune Matrix"
    ],
    "Task": [
        "Balance Moonledger Entries",
        "Verify Wardkey Grants",
        "Inscribe Venture Hindwaking",
        "Refresh Crisislink Registry",
        "Tune Echofield Array",
        "Draft Quartertide Treasurescope",
        "Examine Accord Parchments",
        "Arrange Patron Dialogues",
        "Refine Pollstream Tallies",
        "Attest Purveyor Sigils",
        "Collate Breachwake Dispatches",
        "Mirror Vital Gnosisvaults",
        "Refresh Ingress Scrollset",
        "Trial Enginefield Throughput",
        "Balance Stockveil Gaps",
        "Inscribe Edict Revisions",
        "Settle Coinback Petitions",
        "Attest Streamshift Outcomes",
        "Marshal Crossband Convocation",
        "Examine Pact Reaffirmance",
        "Render Moonledger Instrumentpane",
        "Rehearse Ruinrollback Rite",
        "Seal Hourtally Ledgers",
        "Inter Finished Venturefolios",
        "Allot Patronhood Mantles",
        "Watch Servicetide Accords",
        "Assemble Verdict Provenance",
        "Inscribe Linkfane Procession",
        "Mirror alternate Threlflow scenarios",
        "Trace Choicewake dependencies",
        "Weigh Oracle driftmarks",
        "Chart Codexgeld lacunae",
        "Align crossthread Gnosislexica",
        "Curate Pulsewake training troves",
        "Strain-prove Marshal accords",
        "Parse Echocircle ruptures",
        "Restitch chronaveil transitions",
        "Calibrate Pactweave thresholds",
        "Attest Vhelmere data fidelity",
        "Profile Gazefield allocation weaves",
        "Shape Breachwake escalation paths",
        "Audit Cipheroth decision trails",
        "Harmonize Goalfan tradeoffs",
        "Assess Threldric handoff integrity",
        "Tune Skewmark detection acuity",
        "Inscribe Driftwake behavior cases",
        "Review Oracle-attend overrides",
        "Benchmark Driftflow response latency",
        "Verify Originwell metadata chains",
        "Weigh Edict execution drift"
    ],
    "TimePeriod": [
        "Thirdquartertide of Cycle 8024",
        "The Rekindling Epoch",
        "Ninthveil Decade",
        "Ledger Cycle 8025",
        "The Afteraccord Decade",
        "The First Bronzewake",
        "The Waning Pillarage",
        "The Candlemind Epoch",
        "The Ironlace Reign",
        "The First Smokewake",
        "The Frostaccord Years",
        "The Skyvault Scramble",
        "The First Glyphsignal Wave",
        "The Tenthmilepost Shift",
        "The Gildcorner Twenties",
        "The Hollowledger Years",
        "The Aftersmoke Epoch",
        "The First Modernfold",
        "Age of Horizonhunt",
        "The Tallkeep Mid-Age",
        "The Waning Ancient Fold",
        "The First Thronewake",
        "The Betweenaccord Years",
        "The Gnosis Epoch",
        "The Corebreak Epoch",
        "The Afterfrost Epoch",
        "The First Century of the Third Mile",
        "The Contagionshroud Epoch",
        "The Age of Convergence",
        "Era of Silent Networks",
        "The Long Calibration",
        "Period of Fractured Consensus",
        "The Adaptive Century",
        "The Era of Soft Systems",
        "Time of Emergent Signals",
        "The Coordinated Decades",
        "Age of Context Collapse",
        "The Reflective Interval",
        "The Latent Expansion",
        "Epoch of Distributed Memory",
        "The Harmonization Period",
        "The Provisional Age",
        "The Synthesis Years",
        "Era of Recursive Design",
        "The Threshold Interval",
        "The Continuity Phase",
        "Age of Signal Drift",
        "The Transitional Century",
        "The Quiet Acceleration",
        "Era of Layered Time"
    ]
}

# Grammar templates for natural language generation
# Each relation has:
#   - "statement": Template for "{e1} [relation] {e2}." statement
#   - "question": Template for asking about {e2} given {e1}
#   - "relative": Template for multi-hop: "the {domain} that [relation] {e1}"
#
# Placeholders: {e1} = entity1, {e2} = entity2, {domain} = target domain (lowercase)

RELATION_TEMPLATES = {

    # ==================== SAME-DOMAIN RELATIONS ====================
    # (none — every relation in RELATION_SCHEMA is cross-domain)

    # ==================== CROSS-DOMAIN RELATIONS ====================

    # ---------- Person ↔ Location ----------
    "resides_in": {
        "statement": "{e1} resides in the location {e2}.",
        "question": "What location does {e1} reside in?",
        "relative": "the location {e1} resides in",
    },
    "visits": {
        "statement": "{e1} visits the location {e2}.",
        "question": "What location does {e1} visit?",
        "relative": "the location {e1} visits",
    },
    "was_born_in": {
        "statement": "{e1} was born in the location {e2}.",
        "question": "What location was {e1} born in?",
        "relative": "the location {e1} was born in",
    },
    "works_in": {
        "statement": "{e1} works in the location {e2}.",
        "question": "What location does {e1} work in?",
        "relative": "the location {e1} works in",
    },
    "relocated_to": {
        "statement": "{e1} relocated to the location {e2}.",
        "question": "What location did {e1} relocate to?",
        "relative": "the location {e1} relocated to",
    },
    "is_from": {
        "statement": "{e1} is from the location {e2}.",
        "question": "What location is {e1} from?",
        "relative": "the location {e1} is from",
    },
    "commutes_to": {
        "statement": "{e1} commutes to the location {e2}.",
        "question": "What location does {e1} commute to?",
        "relative": "the location {e1} commutes to",
    },
    "vacations_in": {
        "statement": "{e1} vacations in the location {e2}.",
        "question": "What location does {e1} vacation in?",
        "relative": "the location {e1} vacations in",
    },
    "is_stranded_in": {
        "statement": "{e1} is stranded in the location {e2}.",
        "question": "What location is {e1} stranded in?",
        "relative": "the location {e1} is stranded in",
    },
    "explores": {
        "statement": "{e1} explores the location {e2}.",
        "question": "What location does {e1} explore?",
        "relative": "the location {e1} explores",
    },

    # ---------- Person ↔ Organization ----------
    "is_employed_by": {
        "statement": "{e1} is employed by the organization {e2}.",
        "question": "What organization employs {e1}?",
        "relative": "the organization that employs {e1}",
    },
    "is_member_of": {
        "statement": "{e1} is a member of the organization {e2}.",
        "question": "What organization is {e1} a member of?",
        "relative": "the organization {e1} is a member of",
    },
    "founded": {
        "statement": "{e1} founded the organization {e2}.",
        "question": "What organization did {e1} found?",
        "relative": "the organization {e1} founded",
    },
    "advises": {
        "statement": "{e1} advises the organization {e2}.",
        "question": "What organization does {e1} advise?",
        "relative": "the organization {e1} advises",
    },
    "invests_in": {
        "statement": "{e1} invests in the organization {e2}.",
        "question": "What organization does {e1} invest in?",
        "relative": "the organization {e1} invests in",
    },
    "volunteers_for": {
        "statement": "{e1} volunteers for the organization {e2}.",
        "question": "What organization does {e1} volunteer for?",
        "relative": "the organization {e1} volunteers for",
    },
    "consults_for": {
        "statement": "{e1} consults for the organization {e2}.",
        "question": "What organization does {e1} consult for?",
        "relative": "the organization {e1} consults for",
    },
    "is_board_member_of": {
        "statement": "{e1} is a board member of the organization {e2}.",
        "question": "What organization is {e1} a board member of?",
        "relative": "the organization {e1} is a board member of",
    },
    "was_fired_by": {
        "statement": "{e1} was fired by the organization {e2}.",
        "question": "What organization fired {e1}?",
        "relative": "the organization that fired {e1}",
    },
    "is_alumni_of": {
        "statement": "{e1} is an alumni of the organization {e2}.",
        "question": "What organization is {e1} an alumni of?",
        "relative": "the organization {e1} is an alumni of",
    },

    # ---------- Person ↔ Event ----------
    "participates_in": {
        "statement": "{e1} participates in the event {e2}.",
        "question": "What event does {e1} participate in?",
        "relative": "the event {e1} participates in",
    },
    "organizes": {
        "statement": "{e1} organizes the event {e2}.",
        "question": "What event does {e1} organize?",
        "relative": "the event {e1} organizes",
    },
    "attends": {
        "statement": "{e1} attends the event {e2}.",
        "question": "What event does {e1} attend?",
        "relative": "the event {e1} attends",
    },
    "speaks_at": {
        "statement": "{e1} speaks at the event {e2}.",
        "question": "What event does {e1} speak at?",
        "relative": "the event {e1} speaks at",
    },
    "sponsors": {
        "statement": "{e1} sponsors the event {e2}.",
        "question": "What event does {e1} sponsor?",
        "relative": "the event {e1} sponsors",
    },
    "judges": {
        "statement": "{e1} judges the event {e2}.",
        "question": "What event does {e1} judge?",
        "relative": "the event {e1} judges",
    },
    "volunteers_at": {
        "statement": "{e1} volunteers at the event {e2}.",
        "question": "What event does {e1} volunteer at?",
        "relative": "the event {e1} volunteers at",
    },
    "is_honored_at": {
        "statement": "{e1} is honored at the event {e2}.",
        "question": "What event is {e1} honored at?",
        "relative": "the event {e1} is honored at",
    },
    "boycotts": {
        "statement": "{e1} boycotts the event {e2}.",
        "question": "What event does {e1} boycott?",
        "relative": "the event {e1} boycotts",
    },
    "is_excluded_from": {
        "statement": "{e1} is excluded from the event {e2}.",
        "question": "What event is {e1} excluded from?",
        "relative": "the event {e1} is excluded from",
    },

    # ---------- Person ↔ Profession ----------
    "practices": {
        "statement": "{e1} practices the profession {e2}.",
        "question": "What profession does {e1} practice?",
        "relative": "the profession {e1} practices",
    },
    "studies": {
        "statement": "{e1} studies the profession {e2}.",
        "question": "What profession does {e1} study?",
        "relative": "the profession {e1} studies",
    },
    "retired_from": {
        "statement": "{e1} retired from the profession {e2}.",
        "question": "What profession did {e1} retire from?",
        "relative": "the profession {e1} retired from",
    },
    "is_certified_in": {
        "statement": "{e1} is certified in the profession {e2}.",
        "question": "What profession is {e1} certified in?",
        "relative": "the profession {e1} is certified in",
    },
    "is_training_for": {
        "statement": "{e1} is training for the profession {e2}.",
        "question": "What profession is {e1} training for?",
        "relative": "the profession {e1} is training for",
    },
    "transitioned_from": {
        "statement": "{e1} transitioned from the profession {e2}.",
        "question": "What profession did {e1} transition from?",
        "relative": "the profession {e1} transitioned from",
    },
    "excels_at": {
        "statement": "{e1} excels at the profession {e2}.",
        "question": "What profession does {e1} excel at?",
        "relative": "the profession {e1} excels at",
    },
    "struggles_with": {
        "statement": "{e1} struggles with the profession {e2}.",
        "question": "What profession does {e1} struggle with?",
        "relative": "the profession {e1} struggles with",
    },
    "teaches": {
        "statement": "{e1} teaches the profession {e2}.",
        "question": "What profession does {e1} teach?",
        "relative": "the profession {e1} teaches",
    },
    "is_pioneer_in": {
        "statement": "{e1} is a pioneer in the profession {e2}.",
        "question": "What profession is {e1} a pioneer in?",
        "relative": "the profession {e1} is a pioneer in",
    },

    # ---------- Person ↔ Hobby ----------
    "actively_pursues": {
        "statement": "{e1} actively pursues the hobby {e2}.",
        "question": "What hobby does {e1} actively pursue?",
        "relative": "the hobby {e1} activelies pursue",
    },
    "is_interested_in": {
        "statement": "{e1} is interested in the hobby {e2}.",
        "question": "What hobby is {e1} interested in?",
        "relative": "the hobby {e1} is interested in",
    },
    "has_mastered": {
        "statement": "{e1} has mastered the hobby {e2}.",
        "question": "What hobby has {e1} mastered?",
        "relative": "the hobby {e1} has mastered",
    },
    "is_beginner_at": {
        "statement": "{e1} is a beginner at the hobby {e2}.",
        "question": "What hobby is {e1} a beginner at?",
        "relative": "the hobby {e1} is a beginner at",
    },
    "abandoned": {
        "statement": "{e1} abandoned the hobby {e2}.",
        "question": "What hobby did {e1} abandon?",
        "relative": "the hobby {e1} abandoned",
    },
    "teaches_per_hob": {
        "statement": "{e1} teaches the hobby {e2}.",
        "question": "What hobby does {e1} teach?",
        "relative": "the hobby {e1} teaches",
    },
    "competes_in": {
        "statement": "{e1} competes in the hobby {e2}.",
        "question": "What hobby does {e1} compete in?",
        "relative": "the hobby {e1} competes in",
    },
    "discovered": {
        "statement": "{e1} discovered the hobby {e2}.",
        "question": "What hobby did {e1} discover?",
        "relative": "the hobby {e1} discovered",
    },
    "is_obsessed_with": {
        "statement": "{e1} is obsessed with the hobby {e2}.",
        "question": "What hobby is {e1} obsessed with?",
        "relative": "the hobby {e1} is obsessed with",
    },
    "shares": {
        "statement": "{e1} shares the hobby {e2}.",
        "question": "What hobby does {e1} share?",
        "relative": "the hobby {e1} shares",
    },

    # ---------- Person ↔ Skill ----------
    "masters": {
        "statement": "{e1} masters the skill {e2}.",
        "question": "What skill does {e1} master?",
        "relative": "the skill {e1} masters",
    },
    "is_learning": {
        "statement": "{e1} is learning the skill {e2}.",
        "question": "What skill is {e1} learning?",
        "relative": "the skill {e1} is learning",
    },
    "lacks": {
        "statement": "{e1} lacks the skill {e2}.",
        "question": "What skill does {e1} lack?",
        "relative": "the skill {e1} lacks",
    },
    "demonstrates": {
        "statement": "{e1} demonstrates the skill {e2}.",
        "question": "What skill does {e1} demonstrate?",
        "relative": "the skill {e1} demonstrates",
    },
    "teaches_per_skl": {
        "statement": "{e1} teaches the skill {e2}.",
        "question": "What skill does {e1} teach?",
        "relative": "the skill {e1} teaches",
    },
    "is_certified_in_per_skl": {
        "statement": "{e1} is certified in the skill {e2}.",
        "question": "What skill is {e1} certified in?",
        "relative": "the skill {e1} is certified in",
    },
    "is_renowned_for": {
        "statement": "{e1} is renowned for the skill {e2}.",
        "question": "What skill is {e1} renowned for?",
        "relative": "the skill {e1} is renowned for",
    },
    "is_developing": {
        "statement": "{e1} is developing the skill {e2}.",
        "question": "What skill is {e1} developing?",
        "relative": "the skill {e1} is developing",
    },
    "applies": {
        "statement": "{e1} applies the skill {e2}.",
        "question": "What skill does {e1} apply?",
        "relative": "the skill {e1} applies",
    },
    "underestimates": {
        "statement": "{e1} underestimates the skill {e2}.",
        "question": "What skill does {e1} underestimate?",
        "relative": "the skill {e1} underestimates",
    },

    # ---------- Person ↔ PhysicalObject ----------
    "owns": {
        "statement": "{e1} owns the object {e2}.",
        "question": "What object does {e1} own?",
        "relative": "the object {e1} owns",
    },
    "borrows": {
        "statement": "{e1} borrows the object {e2}.",
        "question": "What object does {e1} borrow?",
        "relative": "the object {e1} borrows",
    },
    "uses": {
        "statement": "{e1} uses the object {e2}.",
        "question": "What object does {e1} use?",
        "relative": "the object {e1} uses",
    },
    "repairs": {
        "statement": "{e1} repairs the object {e2}.",
        "question": "What object does {e1} repair?",
        "relative": "the object {e1} repairs",
    },
    "lost": {
        "statement": "{e1} lost the object {e2}.",
        "question": "What object did {e1} lose?",
        "relative": "the object {e1} lost",
    },
    "inherited": {
        "statement": "{e1} inherited the object {e2}.",
        "question": "What object did {e1} inherit?",
        "relative": "the object {e1} inherited",
    },
    "donated": {
        "statement": "{e1} donated the object {e2}.",
        "question": "What object did {e1} donate?",
        "relative": "the object {e1} donated",
    },
    "collects": {
        "statement": "{e1} collects the object {e2}.",
        "question": "What object does {e1} collect?",
        "relative": "the object {e1} collects",
    },
    "crafted": {
        "statement": "{e1} crafted the object {e2}.",
        "question": "What object did {e1} craft?",
        "relative": "the object {e1} crafted",
    },
    "is_searching_for": {
        "statement": "{e1} is searching for the object {e2}.",
        "question": "What object is {e1} searching for?",
        "relative": "the object {e1} is searching for",
    },

    # ---------- Person ↔ Product ----------
    "purchases": {
        "statement": "{e1} purchases the product {e2}.",
        "question": "What product does {e1} purchase?",
        "relative": "the product {e1} purchases",
    },
    "reviews": {
        "statement": "{e1} reviews the product {e2}.",
        "question": "What product does {e1} review?",
        "relative": "the product {e1} reviews",
    },
    "recommends": {
        "statement": "{e1} recommends the product {e2}.",
        "question": "What product does {e1} recommend?",
        "relative": "the product {e1} recommends",
    },
    "returns": {
        "statement": "{e1} returns the product {e2}.",
        "question": "What product does {e1} return?",
        "relative": "the product {e1} returns",
    },
    "invented": {
        "statement": "{e1} invented the product {e2}.",
        "question": "What product did {e1} invent?",
        "relative": "the product {e1} invented",
    },
    "endorses": {
        "statement": "{e1} endorses the product {e2}.",
        "question": "What product does {e1} endorse?",
        "relative": "the product {e1} endorses",
    },
    "is_allergic_to": {
        "statement": "{e1} is allergic to the product {e2}.",
        "question": "What product is {e1} allergic to?",
        "relative": "the product {e1} is allergic to",
    },
    "preorders": {
        "statement": "{e1} preorders the product {e2}.",
        "question": "What product does {e1} preorder?",
        "relative": "the product {e1} preorders",
    },
    "regrets_buying": {
        "statement": "{e1} regrets buying the product {e2}.",
        "question": "What product does {e1} regret buying?",
        "relative": "the product {e1} regrets buying",
    },
    "is_loyal_to": {
        "statement": "{e1} is loyal to the product {e2}.",
        "question": "What product is {e1} loyal to?",
        "relative": "the product {e1} is loyal to",
    },

    # ---------- Person ↔ Service ----------
    "subscribes_to": {
        "statement": "{e1} subscribes to the service {e2}.",
        "question": "What service does {e1} subscribe to?",
        "relative": "the service {e1} subscribes to",
    },
    "provides": {
        "statement": "{e1} provides the service {e2}.",
        "question": "What service does {e1} provide?",
        "relative": "the service {e1} provides",
    },
    "cancels": {
        "statement": "{e1} cancels the service {e2}.",
        "question": "What service does {e1} cancel?",
        "relative": "the service {e1} cancels",
    },
    "recommends_per_svc": {
        "statement": "{e1} recommends the service {e2}.",
        "question": "What service does {e1} recommend?",
        "relative": "the service {e1} recommends",
    },
    "complains_about": {
        "statement": "{e1} complains about the service {e2}.",
        "question": "What service does {e1} complain about?",
        "relative": "the service {e1} complains about",
    },
    "is_waitlisted_for": {
        "statement": "{e1} is waitlisted for the service {e2}.",
        "question": "What service is {e1} waitlisted for?",
        "relative": "the service {e1} is waitlisted for",
    },
    "is_banned_from": {
        "statement": "{e1} is banned from the service {e2}.",
        "question": "What service is {e1} banned from?",
        "relative": "the service {e1} is banned from",
    },
    "relies_on": {
        "statement": "{e1} relies on the service {e2}.",
        "question": "What service does {e1} rely on?",
        "relative": "the service {e1} relies on",
    },
    "rates": {
        "statement": "{e1} rates the service {e2}.",
        "question": "What service does {e1} rate?",
        "relative": "the service {e1} rates",
    },
    "discovered_per_svc": {
        "statement": "{e1} discovered the service {e2}.",
        "question": "What service did {e1} discover?",
        "relative": "the service {e1} discovered",
    },

    # ---------- Person ↔ MediaWork ----------
    "consumes": {
        "statement": "{e1} consumes the media work {e2}.",
        "question": "What media work does {e1} consume?",
        "relative": "the media work {e1} consumes",
    },
    "creates": {
        "statement": "{e1} creates the media work {e2}.",
        "question": "What media work does {e1} create?",
        "relative": "the media work {e1} creates",
    },
    "reviews_per_mda": {
        "statement": "{e1} reviews the media work {e2}.",
        "question": "What media work does {e1} review?",
        "relative": "the media work {e1} reviews",
    },
    "is_featured_in": {
        "statement": "{e1} is featured in the media work {e2}.",
        "question": "What media work is {e1} featured in?",
        "relative": "the media work {e1} is featured in",
    },
    "recommends_per_mda": {
        "statement": "{e1} recommends the media work {e2}.",
        "question": "What media work does {e1} recommend?",
        "relative": "the media work {e1} recommends",
    },
    "criticizes": {
        "statement": "{e1} criticizes the media work {e2}.",
        "question": "What media work does {e1} criticize?",
        "relative": "the media work {e1} criticizes",
    },
    "is_inspired_by": {
        "statement": "{e1} is inspired by the media work {e2}.",
        "question": "What media work inspires {e1}?",
        "relative": "the media work that inspires {e1}",
    },
    "narrates": {
        "statement": "{e1} narrates the media work {e2}.",
        "question": "What media work does {e1} narrate?",
        "relative": "the media work {e1} narrates",
    },
    "translates": {
        "statement": "{e1} translates the media work {e2}.",
        "question": "What media work does {e1} translate?",
        "relative": "the media work {e1} translates",
    },
    "is_obsessed_with_per_mda": {
        "statement": "{e1} is obsessed with the media work {e2}.",
        "question": "What media work is {e1} obsessed with?",
        "relative": "the media work {e1} is obsessed with",
    },

    # ---------- Person ↔ DigitalTool ----------
    "uses_per_dgt": {
        "statement": "{e1} uses the digital tool {e2}.",
        "question": "What digital tool does {e1} use?",
        "relative": "the digital tool {e1} uses",
    },
    "develops": {
        "statement": "{e1} develops the digital tool {e2}.",
        "question": "What digital tool does {e1} develop?",
        "relative": "the digital tool {e1} develops",
    },
    "masters_per_dgt": {
        "statement": "{e1} masters the digital tool {e2}.",
        "question": "What digital tool does {e1} master?",
        "relative": "the digital tool {e1} masters",
    },
    "avoids": {
        "statement": "{e1} avoids the digital tool {e2}.",
        "question": "What digital tool does {e1} avoid?",
        "relative": "the digital tool {e1} avoids",
    },
    "recommends_per_dgt": {
        "statement": "{e1} recommends the digital tool {e2}.",
        "question": "What digital tool does {e1} recommend?",
        "relative": "the digital tool {e1} recommends",
    },
    "is_frustrated_by": {
        "statement": "{e1} is frustrated by the digital tool {e2}.",
        "question": "What digital tool frustrates {e1}?",
        "relative": "the digital tool that frustrates {e1}",
    },
    "is_dependent_on": {
        "statement": "{e1} is dependent on the digital tool {e2}.",
        "question": "What digital tool is {e1} dependent on?",
        "relative": "the digital tool {e1} is dependent on",
    },
    "debugs": {
        "statement": "{e1} debugs the digital tool {e2}.",
        "question": "What digital tool does {e1} debug?",
        "relative": "the digital tool {e1} debugs",
    },
    "customizes": {
        "statement": "{e1} customizes the digital tool {e2}.",
        "question": "What digital tool does {e1} customize?",
        "relative": "the digital tool {e1} customizes",
    },
    "evangelizes": {
        "statement": "{e1} evangelizes the digital tool {e2}.",
        "question": "What digital tool does {e1} evangelize?",
        "relative": "the digital tool {e1} evangelizes",
    },

    # ---------- Person ↔ Task ----------
    "performs": {
        "statement": "{e1} performs the task {e2}.",
        "question": "What task does {e1} perform?",
        "relative": "the task {e1} performs",
    },
    "delegates": {
        "statement": "{e1} delegates the task {e2}.",
        "question": "What task does {e1} delegate?",
        "relative": "the task {e1} delegates",
    },
    "completes": {
        "statement": "{e1} completes the task {e2}.",
        "question": "What task does {e1} complete?",
        "relative": "the task {e1} completes",
    },
    "postpones": {
        "statement": "{e1} postpones the task {e2}.",
        "question": "What task does {e1} postpone?",
        "relative": "the task {e1} postpones",
    },
    "is_assigned": {
        "statement": "{e1} is assigned the task {e2}.",
        "question": "What task is {e1} assigned?",
        "relative": "the task {e1} is assigned",
    },
    "struggles_with_per_tsk": {
        "statement": "{e1} struggles with the task {e2}.",
        "question": "What task does {e1} struggle with?",
        "relative": "the task {e1} struggles with",
    },
    "excels_at_per_tsk": {
        "statement": "{e1} excels at the task {e2}.",
        "question": "What task does {e1} excel at?",
        "relative": "the task {e1} excels at",
    },
    "automates": {
        "statement": "{e1} automates the task {e2}.",
        "question": "What task does {e1} automate?",
        "relative": "the task {e1} automates",
    },
    "documents": {
        "statement": "{e1} documents the task {e2}.",
        "question": "What task does {e1} document?",
        "relative": "the task {e1} documents",
    },
    "is_overwhelmed_by": {
        "statement": "{e1} is overwhelmed by the task {e2}.",
        "question": "What task overwhelms {e1}?",
        "relative": "the task that overwhelms {e1}",
    },

    # ---------- Person ↔ TimePeriod ----------
    "was_born_in_per_tmp": {
        "statement": "{e1} was born in the time period {e2}.",
        "question": "What time period was {e1} born in?",
        "relative": "the time period {e1} was born in",
    },
    "was_active_during": {
        "statement": "{e1} was active during the time period {e2}.",
        "question": "What time period was {e1} active during?",
        "relative": "the time period {e1} was active during",
    },
    "graduated_in": {
        "statement": "{e1} graduated in the time period {e2}.",
        "question": "What time period did {e1} graduate in?",
        "relative": "the time period {e1} graduated in",
    },
    "retired_in": {
        "statement": "{e1} retired in the time period {e2}.",
        "question": "What time period did {e1} retire in?",
        "relative": "the time period {e1} retired in",
    },
    "thrived_during": {
        "statement": "{e1} thrived during the time period {e2}.",
        "question": "What time period did {e1} thrive during?",
        "relative": "the time period {e1} thrived during",
    },
    "struggled_during": {
        "statement": "{e1} struggled during the time period {e2}.",
        "question": "What time period did {e1} struggle during?",
        "relative": "the time period {e1} struggled during",
    },
    "was_influential_in": {
        "statement": "{e1} was influential in the time period {e2}.",
        "question": "What time period was {e1} influential in?",
        "relative": "the time period {e1} was influential in",
    },
    "relocated_during": {
        "statement": "{e1} relocated during the time period {e2}.",
        "question": "What time period did {e1} relocate during?",
        "relative": "the time period {e1} relocated during",
    },
    "was_married_in": {
        "statement": "{e1} was married in the time period {e2}.",
        "question": "What time period was {e1} married in?",
        "relative": "the time period {e1} was married in",
    },
    "passed_away_in": {
        "statement": "{e1} passed away in the time period {e2}.",
        "question": "What time period did {e1} pass away in?",
        "relative": "the time period {e1} passed away in",
    },

    # ---------- Location ↔ Organization ----------
    "is_headquarters_for": {
        "statement": "{e1} is the headquarters for the organization {e2}.",
        "question": "What organization is headquartered in {e1}?",
        "relative": "the organization that is headquartered in {e1}",
    },
    "is_regulated_by": {
        "statement": "{e1} is regulated by the organization {e2}.",
        "question": "What organization regulates {e1}?",
        "relative": "the organization that regulates {e1}",
    },
    "hosts_branch_of": {
        "statement": "{e1} hosts a branch of the organization {e2}.",
        "question": "What organization has a branch in {e1}?",
        "relative": "the organization that has a branch in {e1}",
    },
    "is_serviced_by": {
        "statement": "{e1} is serviced by the organization {e2}.",
        "question": "What organization services {e1}?",
        "relative": "the organization that services {e1}",
    },
    "is_developed_by": {
        "statement": "{e1} is developed by the organization {e2}.",
        "question": "What organization develops {e1}?",
        "relative": "the organization that develops {e1}",
    },
    "is_protected_by": {
        "statement": "{e1} is protected by the organization {e2}.",
        "question": "What organization protects {e1}?",
        "relative": "the organization that protects {e1}",
    },
    "is_polluted_by": {
        "statement": "{e1} is polluted by the organization {e2}.",
        "question": "What organization pollutes {e1}?",
        "relative": "the organization that pollutes {e1}",
    },
    "is_marketed_by": {
        "statement": "{e1} is marketed by the organization {e2}.",
        "question": "What organization markets {e1}?",
        "relative": "the organization that markets {e1}",
    },
    "is_researched_by": {
        "statement": "{e1} is researched by the organization {e2}.",
        "question": "What organization researches {e1}?",
        "relative": "the organization that researches {e1}",
    },
    "is_owned_by": {
        "statement": "{e1} is owned by the organization {e2}.",
        "question": "What organization owns {e1}?",
        "relative": "the organization that owns {e1}",
    },

    # ---------- Location ↔ Event ----------
    "is_venue_for": {
        "statement": "{e1} is the venue for the event {e2}.",
        "question": "What event is held at {e1}?",
        "relative": "the event that is held at {e1}",
    },
    "is_affected_by": {
        "statement": "{e1} is affected by the event {e2}.",
        "question": "What event affects {e1}?",
        "relative": "the event that affects {e1}",
    },
    "is_origin_of": {
        "statement": "{e1} is the origin of the event {e2}.",
        "question": "What event originated in {e1}?",
        "relative": "the event that originated in {e1}",
    },
    "is_destination_for": {
        "statement": "{e1} is a destination for the event {e2}.",
        "question": "What event has {e1} as a destination?",
        "relative": "the event {e1} has as a destination",
    },
    "is_transformed_by": {
        "statement": "{e1} is transformed by the event {e2}.",
        "question": "What event transforms {e1}?",
        "relative": "the event that transforms {e1}",
    },
    "is_commemorated_by": {
        "statement": "{e1} is commemorated by the event {e2}.",
        "question": "What event commemorates {e1}?",
        "relative": "the event that commemorates {e1}",
    },
    "is_damaged_by": {
        "statement": "{e1} is damaged by the event {e2}.",
        "question": "What event damages {e1}?",
        "relative": "the event that damages {e1}",
    },
    "is_celebrated_at": {
        "statement": "{e1} is celebrated at the event {e2}.",
        "question": "What event is celebrated at {e1}?",
        "relative": "the event that is celebrated at {e1}",
    },
    "is_evacuated_during": {
        "statement": "{e1} is evacuated during the event {e2}.",
        "question": "What event is {e1} evacuated during?",
        "relative": "the event {e1} is evacuated during",
    },
    "is_discovered_at": {
        "statement": "{e1} is discovered at the event {e2}.",
        "question": "What event is {e1} discovered at?",
        "relative": "the event {e1} is discovered at",
    },

    # ---------- Location ↔ Profession ----------
    "is_hub_for": {
        "statement": "{e1} is a hub for the profession {e2}.",
        "question": "What profession thrives in {e1}?",
        "relative": "the profession that thrives in {e1}",
    },
    "lacks_loc_pro": {
        "statement": "{e1} lacks the profession {e2}.",
        "question": "What profession does {e1} lack?",
        "relative": "the profession {e1} lacks",
    },
    "attracts": {
        "statement": "{e1} attracts the profession {e2}.",
        "question": "What profession does {e1} attract?",
        "relative": "the profession {e1} attracts",
    },
    "trains": {
        "statement": "{e1} trains the profession {e2}.",
        "question": "What profession does {e1} train?",
        "relative": "the profession {e1} trains",
    },
    "exports": {
        "statement": "{e1} exports the profession {e2}.",
        "question": "What profession does {e1} export?",
        "relative": "the profession {e1} exports",
    },
    "is_dangerous_for": {
        "statement": "{e1} is dangerous for the profession {e2}.",
        "question": "What profession is {e1} dangerous for?",
        "relative": "the profession {e1} is dangerous for",
    },
    "is_ideal_for": {
        "statement": "{e1} is ideal for the profession {e2}.",
        "question": "What profession is {e1} ideal for?",
        "relative": "the profession {e1} is ideal for",
    },
    "regulates": {
        "statement": "{e1} regulates the profession {e2}.",
        "question": "What profession does {e1} regulate?",
        "relative": "the profession {e1} regulates",
    },
    "celebrates": {
        "statement": "{e1} celebrates the profession {e2}.",
        "question": "What profession does {e1} celebrate?",
        "relative": "the profession {e1} celebrates",
    },
    "is_underserved_by": {
        "statement": "{e1} is underserved by the profession {e2}.",
        "question": "What profession underserves {e1}?",
        "relative": "the profession that underserves {e1}",
    },

    # ---------- Location ↔ Hobby ----------
    "is_destination_for_loc_hob": {
        "statement": "{e1} is a destination for the hobby {e2}.",
        "question": "What hobby has {e1} as a destination?",
        "relative": "the hobby {e1} has as a destination",
    },
    "is_unsuitable_for": {
        "statement": "{e1} is unsuitable for the hobby {e2}.",
        "question": "What hobby is {e1} unsuitable for?",
        "relative": "the hobby {e1} is unsuitable for",
    },
    "is_famous_for": {
        "statement": "{e1} is famous for the hobby {e2}.",
        "question": "What hobby is {e1} famous for?",
        "relative": "the hobby {e1} is famous for",
    },
    "restricts": {
        "statement": "{e1} restricts the hobby {e2}.",
        "question": "What hobby does {e1} restrict?",
        "relative": "the hobby {e1} restricts",
    },
    "encourages": {
        "statement": "{e1} encourages the hobby {e2}.",
        "question": "What hobby does {e1} encourage?",
        "relative": "the hobby {e1} encourages",
    },
    "hosts_competitions_for": {
        "statement": "{e1} hosts competitions for the hobby {e2}.",
        "question": "What hobby does {e1} host competitions for?",
        "relative": "the hobby {e1} hosts competitions for",
    },
    "provides_resources_for": {
        "statement": "{e1} provides resources for the hobby {e2}.",
        "question": "What hobby does {e1} provide resources for?",
        "relative": "the hobby {e1} provides resources for",
    },
    "is_birthplace_of": {
        "statement": "{e1} is the birthplace of the hobby {e2}.",
        "question": "What hobby originated in {e1}?",
        "relative": "the hobby that originated in {e1}",
    },
    "is_dangerous_for_loc_hob": {
        "statement": "{e1} is dangerous for the hobby {e2}.",
        "question": "What hobby is {e1} dangerous for?",
        "relative": "the hobby {e1} is dangerous for",
    },
    "is_overlooked_for": {
        "statement": "{e1} is overlooked for the hobby {e2}.",
        "question": "What hobby is {e1} overlooked for?",
        "relative": "the hobby {e1} is overlooked for",
    },

    # ---------- Location ↔ Skill ----------
    "is_known_for": {
        "statement": "{e1} is known for the skill {e2}.",
        "question": "What skill is {e1} known for?",
        "relative": "the skill {e1} is known for",
    },
    "demands": {
        "statement": "{e1} demands the skill {e2}.",
        "question": "What skill does {e1} demand?",
        "relative": "the skill {e1} demands",
    },
    "teaches_loc_skl": {
        "statement": "{e1} teaches the skill {e2}.",
        "question": "What skill does {e1} teach?",
        "relative": "the skill {e1} teaches",
    },
    "lacks_expertise_in": {
        "statement": "{e1} lacks expertise in the skill {e2}.",
        "question": "What skill does {e1} lack expertise in?",
        "relative": "the skill {e1} lacks expertise in",
    },
    "exports_loc_skl": {
        "statement": "{e1} exports the skill {e2}.",
        "question": "What skill does {e1} export?",
        "relative": "the skill {e1} exports",
    },
    "values": {
        "statement": "{e1} values the skill {e2}.",
        "question": "What skill does {e1} value?",
        "relative": "the skill {e1} values",
    },
    "is_training_ground_for": {
        "statement": "{e1} is a training ground for the skill {e2}.",
        "question": "What skill is {e1} a training ground for?",
        "relative": "the skill {e1} is a training ground for",
    },
    "preserves": {
        "statement": "{e1} preserves the skill {e2}.",
        "question": "What skill does {e1} preserve?",
        "relative": "the skill {e1} preserves",
    },
    "is_underserved_in": {
        "statement": "{e1} is underserved in the skill {e2}.",
        "question": "What skill is {e1} underserved in?",
        "relative": "the skill {e1} is underserved in",
    },
    "is_innovating_in": {
        "statement": "{e1} is innovating in the skill {e2}.",
        "question": "What skill is {e1} innovating in?",
        "relative": "the skill {e1} is innovating in",
    },

    # ---------- Location ↔ PhysicalObject ----------
    "contains": {
        "statement": "{e1} contains the object {e2}.",
        "question": "What object does {e1} contain?",
        "relative": "the object {e1} contains",
    },
    "produces": {
        "statement": "{e1} produces the object {e2}.",
        "question": "What object does {e1} produce?",
        "relative": "the object {e1} produces",
    },
    "stores": {
        "statement": "{e1} stores the object {e2}.",
        "question": "What object does {e1} store?",
        "relative": "the object {e1} stores",
    },
    "displays": {
        "statement": "{e1} displays the object {e2}.",
        "question": "What object does {e1} display?",
        "relative": "the object {e1} displays",
    },
    "exports_loc_obj": {
        "statement": "{e1} exports the object {e2}.",
        "question": "What object does {e1} export?",
        "relative": "the object {e1} exports",
    },
    "imports": {
        "statement": "{e1} imports the object {e2}.",
        "question": "What object does {e1} import?",
        "relative": "the object {e1} imports",
    },
    "is_source_of": {
        "statement": "{e1} is a source of the object {e2}.",
        "question": "What object is {e1} a source of?",
        "relative": "the object {e1} is a source of",
    },
    "prohibits": {
        "statement": "{e1} prohibits the object {e2}.",
        "question": "What object does {e1} prohibit?",
        "relative": "the object {e1} prohibits",
    },
    "is_famous_for_loc_obj": {
        "statement": "{e1} is famous for the object {e2}.",
        "question": "What object is {e1} famous for?",
        "relative": "the object {e1} is famous for",
    },
    "recycles": {
        "statement": "{e1} recycles the object {e2}.",
        "question": "What object does {e1} recycle?",
        "relative": "the object {e1} recycles",
    },

    # ---------- Location ↔ Product ----------
    "exports_loc_prd": {
        "statement": "{e1} exports the product {e2}.",
        "question": "What product does {e1} export?",
        "relative": "the product {e1} exports",
    },
    "imports_loc_prd": {
        "statement": "{e1} imports the product {e2}.",
        "question": "What product does {e1} import?",
        "relative": "the product {e1} imports",
    },
    "manufactures": {
        "statement": "{e1} manufactures the product {e2}.",
        "question": "What product does {e1} manufacture?",
        "relative": "the product {e1} manufactures",
    },
    "bans": {
        "statement": "{e1} bans the product {e2}.",
        "question": "What product does {e1} ban?",
        "relative": "the product {e1} bans",
    },
    "is_test_market_for": {
        "statement": "{e1} is a test market for the product {e2}.",
        "question": "What product is {e1} a test market for?",
        "relative": "the product {e1} is a test market for",
    },
    "is_origin_of_loc_prd": {
        "statement": "{e1} is the origin of the product {e2}.",
        "question": "What product originated in {e1}?",
        "relative": "the product that originated in {e1}",
    },
    "distributes": {
        "statement": "{e1} distributes the product {e2}.",
        "question": "What product does {e1} distribute?",
        "relative": "the product {e1} distributes",
    },
    "consumes_loc_prd": {
        "statement": "{e1} consumes the product {e2}.",
        "question": "What product does {e1} consume?",
        "relative": "the product {e1} consumes",
    },
    "taxes": {
        "statement": "{e1} taxes the product {e2}.",
        "question": "What product does {e1} tax?",
        "relative": "the product {e1} taxes",
    },
    "is_saturated_with": {
        "statement": "{e1} is saturated with the product {e2}.",
        "question": "What product is {e1} saturated with?",
        "relative": "the product {e1} is saturated with",
    },

    # ---------- Location ↔ Service ----------
    "offers": {
        "statement": "{e1} offers the service {e2}.",
        "question": "What service does {e1} offer?",
        "relative": "the service {e1} offers",
    },
    "lacks_loc_svc": {
        "statement": "{e1} lacks the service {e2}.",
        "question": "What service does {e1} lack?",
        "relative": "the service {e1} lacks",
    },
    "is_underserved_by_loc_svc": {
        "statement": "{e1} is underserved by the service {e2}.",
        "question": "What service underserves {e1}?",
        "relative": "the service that underserves {e1}",
    },
    "regulates_loc_svc": {
        "statement": "{e1} regulates the service {e2}.",
        "question": "What service does {e1} regulate?",
        "relative": "the service {e1} regulates",
    },
    "subsidizes": {
        "statement": "{e1} subsidizes the service {e2}.",
        "question": "What service does {e1} subsidize?",
        "relative": "the service {e1} subsidizes",
    },
    "bans_loc_svc": {
        "statement": "{e1} bans the service {e2}.",
        "question": "What service does {e1} ban?",
        "relative": "the service {e1} bans",
    },
    "is_pioneer_of": {
        "statement": "{e1} is a pioneer of the service {e2}.",
        "question": "What service is {e1} a pioneer of?",
        "relative": "the service {e1} is a pioneer of",
    },
    "outsources": {
        "statement": "{e1} outsources the service {e2}.",
        "question": "What service does {e1} outsource?",
        "relative": "the service {e1} outsources",
    },
    "is_dependent_on_loc_svc": {
        "statement": "{e1} is dependent on the service {e2}.",
        "question": "What service is {e1} dependent on?",
        "relative": "the service {e1} is dependent on",
    },
    "is_gateway_for": {
        "statement": "{e1} is a gateway for the service {e2}.",
        "question": "What service is {e1} a gateway for?",
        "relative": "the service {e1} is a gateway for",
    },

    # ---------- Location ↔ MediaWork ----------
    "is_setting_of": {
        "statement": "{e1} is the setting of the media work {e2}.",
        "question": "What media work is set in {e1}?",
        "relative": "the media work that is set in {e1}",
    },
    "is_subject_of": {
        "statement": "{e1} is the subject of the media work {e2}.",
        "question": "What media work is {e1} the subject of?",
        "relative": "the media work {e1} is the subject of",
    },
    "is_filming_location_for": {
        "statement": "{e1} is a filming location for the media work {e2}.",
        "question": "What media work was filmed in {e1}?",
        "relative": "the media work that was filmed in {e1}",
    },
    "inspired": {
        "statement": "{e1} inspired the media work {e2}.",
        "question": "What media work did {e1} inspire?",
        "relative": "the media work {e1} inspired",
    },
    "is_featured_in_loc_mda": {
        "statement": "{e1} is featured in the media work {e2}.",
        "question": "What media work is {e1} featured in?",
        "relative": "the media work {e1} is featured in",
    },
    "is_misrepresented_in": {
        "statement": "{e1} is misrepresented in the media work {e2}.",
        "question": "What media work misrepresents {e1}?",
        "relative": "the media work that misrepresents {e1}",
    },
    "bans_loc_mda": {
        "statement": "{e1} bans the media work {e2}.",
        "question": "What media work does {e1} ban?",
        "relative": "the media work {e1} bans",
    },
    "celebrates_loc_mda": {
        "statement": "{e1} celebrates the media work {e2}.",
        "question": "What media work does {e1} celebrate?",
        "relative": "the media work {e1} celebrates",
    },
    "is_documented_in": {
        "statement": "{e1} is documented in the media work {e2}.",
        "question": "What media work documents {e1}?",
        "relative": "the media work that documents {e1}",
    },
    "preserves_loc_mda": {
        "statement": "{e1} preserves the media work {e2}.",
        "question": "What media work does {e1} preserve?",
        "relative": "the media work {e1} preserves",
    },

    # ---------- Location ↔ DigitalTool ----------
    "is_coverage_area_of": {
        "statement": "{e1} is a coverage area of the digital tool {e2}.",
        "question": "What digital tool covers {e1}?",
        "relative": "the digital tool that covers {e1}",
    },
    "is_underserved_by_loc_dgt": {
        "statement": "{e1} is underserved by the digital tool {e2}.",
        "question": "What digital tool underserves {e1}?",
        "relative": "the digital tool that underserves {e1}",
    },
    "bans_loc_dgt": {
        "statement": "{e1} bans the digital tool {e2}.",
        "question": "What digital tool does {e1} ban?",
        "relative": "the digital tool {e1} bans",
    },
    "is_test_market_for_loc_dgt": {
        "statement": "{e1} is a test market for the digital tool {e2}.",
        "question": "What digital tool is {e1} a test market for?",
        "relative": "the digital tool {e1} is a test market for",
    },
    "adopts": {
        "statement": "{e1} adopts the digital tool {e2}.",
        "question": "What digital tool does {e1} adopt?",
        "relative": "the digital tool {e1} adopts",
    },
    "regulates_loc_dgt": {
        "statement": "{e1} regulates the digital tool {e2}.",
        "question": "What digital tool does {e1} regulate?",
        "relative": "the digital tool {e1} regulates",
    },
    "is_development_hub_for": {
        "statement": "{e1} is a development hub for the digital tool {e2}.",
        "question": "What digital tool is developed in {e1}?",
        "relative": "the digital tool that is developed in {e1}",
    },
    "is_dependent_on_loc_dgt": {
        "statement": "{e1} is dependent on the digital tool {e2}.",
        "question": "What digital tool is {e1} dependent on?",
        "relative": "the digital tool {e1} is dependent on",
    },
    "subsidizes_loc_dgt": {
        "statement": "{e1} subsidizes the digital tool {e2}.",
        "question": "What digital tool does {e1} subsidize?",
        "relative": "the digital tool {e1} subsidizes",
    },
    "is_mapped_by": {
        "statement": "{e1} is mapped by the digital tool {e2}.",
        "question": "What digital tool maps {e1}?",
        "relative": "the digital tool that maps {e1}",
    },

    # ---------- Location ↔ Task ----------
    "is_site_of": {
        "statement": "{e1} is a site of the task {e2}.",
        "question": "What task happens at {e1}?",
        "relative": "the task that happens at {e1}",
    },
    "restricts_loc_tsk": {
        "statement": "{e1} restricts the task {e2}.",
        "question": "What task does {e1} restrict?",
        "relative": "the task {e1} restricts",
    },
    "requires": {
        "statement": "{e1} requires the task {e2}.",
        "question": "What task does {e1} require?",
        "relative": "the task {e1} requires",
    },
    "facilitates": {
        "statement": "{e1} facilitates the task {e2}.",
        "question": "What task does {e1} facilitate?",
        "relative": "the task {e1} facilitates",
    },
    "complicates": {
        "statement": "{e1} complicates the task {e2}.",
        "question": "What task does {e1} complicate?",
        "relative": "the task {e1} complicates",
    },
    "is_optimized_for": {
        "statement": "{e1} is optimized for the task {e2}.",
        "question": "What task is {e1} optimized for?",
        "relative": "the task {e1} is optimized for",
    },
    "prohibits_loc_tsk": {
        "statement": "{e1} prohibits the task {e2}.",
        "question": "What task does {e1} prohibit?",
        "relative": "the task {e1} prohibits",
    },
    "is_staging_area_for": {
        "statement": "{e1} is a staging area for the task {e2}.",
        "question": "What task is {e1} a staging area for?",
        "relative": "the task {e1} is a staging area for",
    },
    "automates_loc_tsk": {
        "statement": "{e1} automates the task {e2}.",
        "question": "What task does {e1} automate?",
        "relative": "the task {e1} automates",
    },
    "outsources_loc_tsk": {
        "statement": "{e1} outsources the task {e2}.",
        "question": "What task does {e1} outsource?",
        "relative": "the task {e1} outsources",
    },

    # ---------- Location ↔ TimePeriod ----------
    "was_founded_in": {
        "statement": "{e1} was founded in the time period {e2}.",
        "question": "What time period was {e1} founded in?",
        "relative": "the time period {e1} was founded in",
    },
    "was_transformed_during": {
        "statement": "{e1} was transformed during the time period {e2}.",
        "question": "What time period was {e1} transformed during?",
        "relative": "the time period {e1} was transformed during",
    },
    "flourished_during": {
        "statement": "{e1} flourished during the time period {e2}.",
        "question": "What time period did {e1} flourish during?",
        "relative": "the time period {e1} flourished during",
    },
    "declined_during": {
        "statement": "{e1} declined during the time period {e2}.",
        "question": "What time period did {e1} decline during?",
        "relative": "the time period {e1} declined during",
    },
    "was_discovered_in": {
        "statement": "{e1} was discovered in the time period {e2}.",
        "question": "What time period was {e1} discovered in?",
        "relative": "the time period {e1} was discovered in",
    },
    "was_destroyed_in": {
        "statement": "{e1} was destroyed in the time period {e2}.",
        "question": "What time period was {e1} destroyed in?",
        "relative": "the time period {e1} was destroyed in",
    },
    "was_rebuilt_in": {
        "statement": "{e1} was rebuilt in the time period {e2}.",
        "question": "What time period was {e1} rebuilt in?",
        "relative": "the time period {e1} was rebuilt in",
    },
    "was_renamed_in": {
        "statement": "{e1} was renamed in the time period {e2}.",
        "question": "What time period was {e1} renamed in?",
        "relative": "the time period {e1} was renamed in",
    },
    "was_colonized_in": {
        "statement": "{e1} was colonized in the time period {e2}.",
        "question": "What time period was {e1} colonized in?",
        "relative": "the time period {e1} was colonized in",
    },
    "gained_independence_in": {
        "statement": "{e1} gained independence in the time period {e2}.",
        "question": "What time period did {e1} gain independence in?",
        "relative": "the time period {e1} gained independence in",
    },

    # ---------- Organization ↔ Event ----------
    "hosts": {
        "statement": "{e1} hosts the event {e2}.",
        "question": "What event does {e1} host?",
        "relative": "the event {e1} hosts",
    },
    "sponsors_org_evt": {
        "statement": "{e1} sponsors the event {e2}.",
        "question": "What event does {e1} sponsor?",
        "relative": "the event {e1} sponsors",
    },
    "organizes_org_evt": {
        "statement": "{e1} organizes the event {e2}.",
        "question": "What event does {e1} organize?",
        "relative": "the event {e1} organizes",
    },
    "participates_in_org_evt": {
        "statement": "{e1} participates in the event {e2}.",
        "question": "What event does {e1} participate in?",
        "relative": "the event {e1} participates in",
    },
    "boycotts_org_evt": {
        "statement": "{e1} boycotts the event {e2}.",
        "question": "What event does {e1} boycott?",
        "relative": "the event {e1} boycotts",
    },
    "is_honored_at_org_evt": {
        "statement": "{e1} is honored at the event {e2}.",
        "question": "What event is {e1} honored at?",
        "relative": "the event {e1} is honored at",
    },
    "is_criticized_at": {
        "statement": "{e1} is criticized at the event {e2}.",
        "question": "What event is {e1} criticized at?",
        "relative": "the event {e1} is criticized at",
    },
    "announces_at": {
        "statement": "{e1} announces at the event {e2}.",
        "question": "What event does {e1} announce at?",
        "relative": "the event {e1} announces at",
    },
    "recruits_at": {
        "statement": "{e1} recruits at the event {e2}.",
        "question": "What event does {e1} recruit at?",
        "relative": "the event {e1} recruits at",
    },
    "withdraws_from": {
        "statement": "{e1} withdraws from the event {e2}.",
        "question": "What event does {e1} withdraw from?",
        "relative": "the event {e1} withdraws from",
    },

    # ---------- Organization ↔ Profession ----------
    "employs": {
        "statement": "{e1} employs the profession {e2}.",
        "question": "What profession does {e1} employ?",
        "relative": "the profession {e1} employs",
    },
    "certifies": {
        "statement": "{e1} certifies the profession {e2}.",
        "question": "What profession does {e1} certify?",
        "relative": "the profession {e1} certifies",
    },
    "trains_org_pro": {
        "statement": "{e1} trains the profession {e2}.",
        "question": "What profession does {e1} train?",
        "relative": "the profession {e1} trains",
    },
    "lobbies_for": {
        "statement": "{e1} lobbies for the profession {e2}.",
        "question": "What profession does {e1} lobby for?",
        "relative": "the profession {e1} lobbies for",
    },
    "regulates_org_pro": {
        "statement": "{e1} regulates the profession {e2}.",
        "question": "What profession does {e1} regulate?",
        "relative": "the profession {e1} regulates",
    },
    "outsources_org_pro": {
        "statement": "{e1} outsources the profession {e2}.",
        "question": "What profession does {e1} outsource?",
        "relative": "the profession {e1} outsources",
    },
    "automates_org_pro": {
        "statement": "{e1} automates the profession {e2}.",
        "question": "What profession does {e1} automate?",
        "relative": "the profession {e1} automates",
    },
    "recruits": {
        "statement": "{e1} recruits the profession {e2}.",
        "question": "What profession does {e1} recruit?",
        "relative": "the profession {e1} recruits",
    },
    "is_dominated_by": {
        "statement": "{e1} is dominated by the profession {e2}.",
        "question": "What profession dominates {e1}?",
        "relative": "the profession that dominates {e1}",
    },
    "undervalues": {
        "statement": "{e1} undervalues the profession {e2}.",
        "question": "What profession does {e1} undervalue?",
        "relative": "the profession {e1} undervalues",
    },

    # ---------- Organization ↔ Hobby ----------
    "facilitates_org_hob": {
        "statement": "{e1} facilitates the hobby {e2}.",
        "question": "What hobby does {e1} facilitate?",
        "relative": "the hobby {e1} facilitates",
    },
    "prohibits_org_hob": {
        "statement": "{e1} prohibits the hobby {e2}.",
        "question": "What hobby does {e1} prohibit?",
        "relative": "the hobby {e1} prohibits",
    },
    "sponsors_org_hob": {
        "statement": "{e1} sponsors the hobby {e2}.",
        "question": "What hobby does {e1} sponsor?",
        "relative": "the hobby {e1} sponsors",
    },
    "monetizes": {
        "statement": "{e1} monetizes the hobby {e2}.",
        "question": "What hobby does {e1} monetize?",
        "relative": "the hobby {e1} monetizes",
    },
    "promotes": {
        "statement": "{e1} promotes the hobby {e2}.",
        "question": "What hobby does {e1} promote?",
        "relative": "the hobby {e1} promotes",
    },
    "hosts_events_for": {
        "statement": "{e1} hosts events for the hobby {e2}.",
        "question": "What hobby does {e1} host events for?",
        "relative": "the hobby {e1} hosts events for",
    },
    "provides_resources_for_org_hob": {
        "statement": "{e1} provides resources for the hobby {e2}.",
        "question": "What hobby does {e1} provide resources for?",
        "relative": "the hobby {e1} provides resources for",
    },
    "regulates_org_hob": {
        "statement": "{e1} regulates the hobby {e2}.",
        "question": "What hobby does {e1} regulate?",
        "relative": "the hobby {e1} regulates",
    },
    "discourages": {
        "statement": "{e1} discourages the hobby {e2}.",
        "question": "What hobby does {e1} discourage?",
        "relative": "the hobby {e1} discourages",
    },
    "is_inspired_by_org_hob": {
        "statement": "{e1} is inspired by the hobby {e2}.",
        "question": "What hobby inspires {e1}?",
        "relative": "the hobby that inspires {e1}",
    },

    # ---------- Organization ↔ Skill ----------
    "requires_org_skl": {
        "statement": "{e1} requires the skill {e2}.",
        "question": "What skill does {e1} require?",
        "relative": "the skill {e1} requires",
    },
    "teaches_org_skl": {
        "statement": "{e1} teaches the skill {e2}.",
        "question": "What skill does {e1} teach?",
        "relative": "the skill {e1} teaches",
    },
    "certifies_org_skl": {
        "statement": "{e1} certifies the skill {e2}.",
        "question": "What skill does {e1} certify?",
        "relative": "the skill {e1} certifies",
    },
    "values_org_skl": {
        "statement": "{e1} values the skill {e2}.",
        "question": "What skill does {e1} value?",
        "relative": "the skill {e1} values",
    },
    "lacks_org_skl": {
        "statement": "{e1} lacks the skill {e2}.",
        "question": "What skill does {e1} lack?",
        "relative": "the skill {e1} lacks",
    },
    "develops_org_skl": {
        "statement": "{e1} develops the skill {e2}.",
        "question": "What skill does {e1} develop?",
        "relative": "the skill {e1} develops",
    },
    "outsources_org_skl": {
        "statement": "{e1} outsources the skill {e2}.",
        "question": "What skill does {e1} outsource?",
        "relative": "the skill {e1} outsources",
    },
    "automates_org_skl": {
        "statement": "{e1} automates the skill {e2}.",
        "question": "What skill does {e1} automate?",
        "relative": "the skill {e1} automates",
    },
    "benchmarks": {
        "statement": "{e1} benchmarks the skill {e2}.",
        "question": "What skill does {e1} benchmark?",
        "relative": "the skill {e1} benchmarks",
    },
    "is_renowned_for_org_skl": {
        "statement": "{e1} is renowned for the skill {e2}.",
        "question": "What skill is {e1} renowned for?",
        "relative": "the skill {e1} is renowned for",
    },

    # ---------- Organization ↔ PhysicalObject ----------
    "owns_org_obj": {
        "statement": "{e1} owns the object {e2}.",
        "question": "What object does {e1} own?",
        "relative": "the object {e1} owns",
    },
    "leases": {
        "statement": "{e1} leases the object {e2}.",
        "question": "What object does {e1} lease?",
        "relative": "the object {e1} leases",
    },
    "manufactures_org_obj": {
        "statement": "{e1} manufactures the object {e2}.",
        "question": "What object does {e1} manufacture?",
        "relative": "the object {e1} manufactures",
    },
    "distributes_org_obj": {
        "statement": "{e1} distributes the object {e2}.",
        "question": "What object does {e1} distribute?",
        "relative": "the object {e1} distributes",
    },
    "recycles_org_obj": {
        "statement": "{e1} recycles the object {e2}.",
        "question": "What object does {e1} recycle?",
        "relative": "the object {e1} recycles",
    },
    "donates": {
        "statement": "{e1} donates the object {e2}.",
        "question": "What object does {e1} donate?",
        "relative": "the object {e1} donates",
    },
    "imports_org_obj": {
        "statement": "{e1} imports the object {e2}.",
        "question": "What object does {e1} import?",
        "relative": "the object {e1} imports",
    },
    "exports_org_obj": {
        "statement": "{e1} exports the object {e2}.",
        "question": "What object does {e1} export?",
        "relative": "the object {e1} exports",
    },
    "repairs_org_obj": {
        "statement": "{e1} repairs the object {e2}.",
        "question": "What object does {e1} repair?",
        "relative": "the object {e1} repairs",
    },
    "auctions": {
        "statement": "{e1} auctions the object {e2}.",
        "question": "What object does {e1} auction?",
        "relative": "the object {e1} auctions",
    },

    # ---------- Organization ↔ Product ----------
    "manufactures_org_prd": {
        "statement": "{e1} manufactures the product {e2}.",
        "question": "What product does {e1} manufacture?",
        "relative": "the product {e1} manufactures",
    },
    "distributes_org_prd": {
        "statement": "{e1} distributes the product {e2}.",
        "question": "What product does {e1} distribute?",
        "relative": "the product {e1} distributes",
    },
    "markets": {
        "statement": "{e1} markets the product {e2}.",
        "question": "What product does {e1} market?",
        "relative": "the product {e1} markets",
    },
    "recalls": {
        "statement": "{e1} recalls the product {e2}.",
        "question": "What product does {e1} recall?",
        "relative": "the product {e1} recalls",
    },
    "discontinues": {
        "statement": "{e1} discontinues the product {e2}.",
        "question": "What product does {e1} discontinue?",
        "relative": "the product {e1} discontinues",
    },
    "licenses": {
        "statement": "{e1} licenses the product {e2}.",
        "question": "What product does {e1} license?",
        "relative": "the product {e1} licenses",
    },
    "endorses_org_prd": {
        "statement": "{e1} endorses the product {e2}.",
        "question": "What product does {e1} endorse?",
        "relative": "the product {e1} endorses",
    },
    "tests": {
        "statement": "{e1} tests the product {e2}.",
        "question": "What product does {e1} test?",
        "relative": "the product {e1} tests",
    },
    "counterfeits": {
        "statement": "{e1} counterfeits the product {e2}.",
        "question": "What product does {e1} counterfeit?",
        "relative": "the product {e1} counterfeits",
    },
    "reviews_org_prd": {
        "statement": "{e1} reviews the product {e2}.",
        "question": "What product does {e1} review?",
        "relative": "the product {e1} reviews",
    },

    # ---------- Organization ↔ Service ----------
    "provides_org_svc": {
        "statement": "{e1} provides the service {e2}.",
        "question": "What service does {e1} provide?",
        "relative": "the service {e1} provides",
    },
    "outsources_org_svc": {
        "statement": "{e1} outsources the service {e2}.",
        "question": "What service does {e1} outsource?",
        "relative": "the service {e1} outsources",
    },
    "subscribes_to_org_svc": {
        "statement": "{e1} subscribes to the service {e2}.",
        "question": "What service does {e1} subscribe to?",
        "relative": "the service {e1} subscribes to",
    },
    "discontinues_org_svc": {
        "statement": "{e1} discontinues the service {e2}.",
        "question": "What service does {e1} discontinue?",
        "relative": "the service {e1} discontinues",
    },
    "regulates_org_svc": {
        "statement": "{e1} regulates the service {e2}.",
        "question": "What service does {e1} regulate?",
        "relative": "the service {e1} regulates",
    },
    "monopolizes": {
        "statement": "{e1} monopolizes the service {e2}.",
        "question": "What service does {e1} monopolize?",
        "relative": "the service {e1} monopolizes",
    },
    "bundles": {
        "statement": "{e1} bundles the service {e2}.",
        "question": "What service does {e1} bundle?",
        "relative": "the service {e1} bundles",
    },
    "reviews_org_svc": {
        "statement": "{e1} reviews the service {e2}.",
        "question": "What service does {e1} review?",
        "relative": "the service {e1} reviews",
    },
    "integrates": {
        "statement": "{e1} integrates the service {e2}.",
        "question": "What service does {e1} integrate?",
        "relative": "the service {e1} integrates",
    },
    "subsidizes_org_svc": {
        "statement": "{e1} subsidizes the service {e2}.",
        "question": "What service does {e1} subsidize?",
        "relative": "the service {e1} subsidizes",
    },

    # ---------- Organization ↔ MediaWork ----------
    "publishes": {
        "statement": "{e1} publishes the media work {e2}.",
        "question": "What media work does {e1} publish?",
        "relative": "the media work {e1} publishes",
    },
    "commissions": {
        "statement": "{e1} commissions the media work {e2}.",
        "question": "What media work does {e1} commission?",
        "relative": "the media work {e1} commissions",
    },
    "sponsors_org_mda": {
        "statement": "{e1} sponsors the media work {e2}.",
        "question": "What media work does {e1} sponsor?",
        "relative": "the media work {e1} sponsors",
    },
    "censors": {
        "statement": "{e1} censors the media work {e2}.",
        "question": "What media work does {e1} censor?",
        "relative": "the media work {e1} censors",
    },
    "distributes_org_mda": {
        "statement": "{e1} distributes the media work {e2}.",
        "question": "What media work does {e1} distribute?",
        "relative": "the media work {e1} distributes",
    },
    "archives": {
        "statement": "{e1} archives the media work {e2}.",
        "question": "What media work does {e1} archive?",
        "relative": "the media work {e1} archives",
    },
    "reviews_org_mda": {
        "statement": "{e1} reviews the media work {e2}.",
        "question": "What media work does {e1} review?",
        "relative": "the media work {e1} reviews",
    },
    "adapts": {
        "statement": "{e1} adapts the media work {e2}.",
        "question": "What media work does {e1} adapt?",
        "relative": "the media work {e1} adapts",
    },
    "is_featured_in_org_mda": {
        "statement": "{e1} is featured in the media work {e2}.",
        "question": "What media work is {e1} featured in?",
        "relative": "the media work {e1} is featured in",
    },
    "sues_over": {
        "statement": "{e1} sues over the media work {e2}.",
        "question": "What media work does {e1} sue over?",
        "relative": "the media work {e1} sues over",
    },

    # ---------- Organization ↔ DigitalTool ----------
    "develops_org_dgt": {
        "statement": "{e1} develops the digital tool {e2}.",
        "question": "What digital tool does {e1} develop?",
        "relative": "the digital tool {e1} develops",
    },
    "licenses_org_dgt": {
        "statement": "{e1} licenses the digital tool {e2}.",
        "question": "What digital tool does {e1} license?",
        "relative": "the digital tool {e1} licenses",
    },
    "deploys": {
        "statement": "{e1} deploys the digital tool {e2}.",
        "question": "What digital tool does {e1} deploy?",
        "relative": "the digital tool {e1} deploys",
    },
    "bans_org_dgt": {
        "statement": "{e1} bans the digital tool {e2}.",
        "question": "What digital tool does {e1} ban?",
        "relative": "the digital tool {e1} bans",
    },
    "acquires": {
        "statement": "{e1} acquires the digital tool {e2}.",
        "question": "What digital tool does {e1} acquire?",
        "relative": "the digital tool {e1} acquires",
    },
    "supports": {
        "statement": "{e1} supports the digital tool {e2}.",
        "question": "What digital tool does {e1} support?",
        "relative": "the digital tool {e1} supports",
    },
    "integrates_org_dgt": {
        "statement": "{e1} integrates the digital tool {e2}.",
        "question": "What digital tool does {e1} integrate?",
        "relative": "the digital tool {e1} integrates",
    },
    "discontinues_org_dgt": {
        "statement": "{e1} discontinues the digital tool {e2}.",
        "question": "What digital tool does {e1} discontinue?",
        "relative": "the digital tool {e1} discontinues",
    },
    "audits": {
        "statement": "{e1} audits the digital tool {e2}.",
        "question": "What digital tool does {e1} audit?",
        "relative": "the digital tool {e1} audits",
    },
    "customizes_org_dgt": {
        "statement": "{e1} customizes the digital tool {e2}.",
        "question": "What digital tool does {e1} customize?",
        "relative": "the digital tool {e1} customizes",
    },

    # ---------- Organization ↔ Task ----------
    "assigns": {
        "statement": "{e1} assigns the task {e2}.",
        "question": "What task does {e1} assign?",
        "relative": "the task {e1} assigns",
    },
    "automates_org_tsk": {
        "statement": "{e1} automates the task {e2}.",
        "question": "What task does {e1} automate?",
        "relative": "the task {e1} automates",
    },
    "outsources_org_tsk": {
        "statement": "{e1} outsources the task {e2}.",
        "question": "What task does {e1} outsource?",
        "relative": "the task {e1} outsources",
    },
    "prioritizes": {
        "statement": "{e1} prioritizes the task {e2}.",
        "question": "What task does {e1} prioritize?",
        "relative": "the task {e1} prioritizes",
    },
    "standardizes": {
        "statement": "{e1} standardizes the task {e2}.",
        "question": "What task does {e1} standardize?",
        "relative": "the task {e1} standardizes",
    },
    "audits_org_tsk": {
        "statement": "{e1} audits the task {e2}.",
        "question": "What task does {e1} audit?",
        "relative": "the task {e1} audits",
    },
    "delays": {
        "statement": "{e1} delays the task {e2}.",
        "question": "What task does {e1} delay?",
        "relative": "the task {e1} delays",
    },
    "streamlines": {
        "statement": "{e1} streamlines the task {e2}.",
        "question": "What task does {e1} streamline?",
        "relative": "the task {e1} streamlines",
    },
    "documents_org_tsk": {
        "statement": "{e1} documents the task {e2}.",
        "question": "What task does {e1} document?",
        "relative": "the task {e1} documents",
    },
    "abandons": {
        "statement": "{e1} abandons the task {e2}.",
        "question": "What task does {e1} abandon?",
        "relative": "the task {e1} abandons",
    },

    # ---------- Organization ↔ TimePeriod ----------
    "was_founded_in_org_tmp": {
        "statement": "{e1} was founded in the time period {e2}.",
        "question": "What time period was {e1} founded in?",
        "relative": "the time period {e1} was founded in",
    },
    "was_dissolved_in": {
        "statement": "{e1} was dissolved in the time period {e2}.",
        "question": "What time period was {e1} dissolved in?",
        "relative": "the time period {e1} was dissolved in",
    },
    "expanded_during": {
        "statement": "{e1} expanded during the time period {e2}.",
        "question": "What time period did {e1} expand during?",
        "relative": "the time period {e1} expanded during",
    },
    "struggled_during_org_tmp": {
        "statement": "{e1} struggled during the time period {e2}.",
        "question": "What time period did {e1} struggle during?",
        "relative": "the time period {e1} struggled during",
    },
    "was_restructured_in": {
        "statement": "{e1} was restructured in the time period {e2}.",
        "question": "What time period was {e1} restructured in?",
        "relative": "the time period {e1} was restructured in",
    },
    "went_public_in": {
        "statement": "{e1} went public in the time period {e2}.",
        "question": "What time period did {e1} go public in?",
        "relative": "the time period {e1} went public in",
    },
    "was_acquired_in": {
        "statement": "{e1} was acquired in the time period {e2}.",
        "question": "What time period was {e1} acquired in?",
        "relative": "the time period {e1} was acquired in",
    },
    "peaked_during": {
        "statement": "{e1} peaked during the time period {e2}.",
        "question": "What time period did {e1} peak during?",
        "relative": "the time period {e1} peaked during",
    },
    "was_sanctioned_in": {
        "statement": "{e1} was sanctioned in the time period {e2}.",
        "question": "What time period was {e1} sanctioned in?",
        "relative": "the time period {e1} was sanctioned in",
    },
    "was_privatized_in": {
        "statement": "{e1} was privatized in the time period {e2}.",
        "question": "What time period was {e1} privatized in?",
        "relative": "the time period {e1} was privatized in",
    },

    # ---------- Event ↔ Profession ----------
    "showcases": {
        "statement": "{e1} showcases the profession {e2}.",
        "question": "What profession does {e1} showcase?",
        "relative": "the profession {e1} showcases",
    },
    "excludes": {
        "statement": "{e1} excludes the profession {e2}.",
        "question": "What profession does {e1} exclude?",
        "relative": "the profession {e1} excludes",
    },
    "honors": {
        "statement": "{e1} honors the profession {e2}.",
        "question": "What profession does {e1} honor?",
        "relative": "the profession {e1} honors",
    },
    "recruits_evt_pro": {
        "statement": "{e1} recruits the profession {e2}.",
        "question": "What profession does {e1} recruit?",
        "relative": "the profession {e1} recruits",
    },
    "trains_evt_pro": {
        "statement": "{e1} trains the profession {e2}.",
        "question": "What profession does {e1} train?",
        "relative": "the profession {e1} trains",
    },
    "debates": {
        "statement": "{e1} debates the profession {e2}.",
        "question": "What profession does {e1} debate?",
        "relative": "the profession {e1} debates",
    },
    "certifies_evt_pro": {
        "statement": "{e1} certifies the profession {e2}.",
        "question": "What profession does {e1} certify?",
        "relative": "the profession {e1} certifies",
    },
    "disrupts": {
        "statement": "{e1} disrupts the profession {e2}.",
        "question": "What profession does {e1} disrupt?",
        "relative": "the profession {e1} disrupts",
    },
    "celebrates_evt_pro": {
        "statement": "{e1} celebrates the profession {e2}.",
        "question": "What profession does {e1} celebrate?",
        "relative": "the profession {e1} celebrates",
    },
    "criticizes_evt_pro": {
        "statement": "{e1} criticizes the profession {e2}.",
        "question": "What profession does {e1} criticize?",
        "relative": "the profession {e1} criticizes",
    },

    # ---------- Event ↔ Hobby ----------
    "celebrates_evt_hob": {
        "statement": "{e1} celebrates the hobby {e2}.",
        "question": "What hobby does {e1} celebrate?",
        "relative": "the hobby {e1} celebrates",
    },
    "features_competition_in": {
        "statement": "{e1} features competition in the hobby {e2}.",
        "question": "What hobby does {e1} feature competition in?",
        "relative": "the hobby {e1} features competition in",
    },
    "promotes_evt_hob": {
        "statement": "{e1} promotes the hobby {e2}.",
        "question": "What hobby does {e1} promote?",
        "relative": "the hobby {e1} promotes",
    },
    "introduces": {
        "statement": "{e1} introduces the hobby {e2}.",
        "question": "What hobby does {e1} introduce?",
        "relative": "the hobby {e1} introduces",
    },
    "bans_evt_hob": {
        "statement": "{e1} bans the hobby {e2}.",
        "question": "What hobby does {e1} ban?",
        "relative": "the hobby {e1} bans",
    },
    "showcases_evt_hob": {
        "statement": "{e1} showcases the hobby {e2}.",
        "question": "What hobby does {e1} showcase?",
        "relative": "the hobby {e1} showcases",
    },
    "awards": {
        "statement": "{e1} awards the hobby {e2}.",
        "question": "What hobby does {e1} award?",
        "relative": "the hobby {e1} awards",
    },
    "monetizes_evt_hob": {
        "statement": "{e1} monetizes the hobby {e2}.",
        "question": "What hobby does {e1} monetize?",
        "relative": "the hobby {e1} monetizes",
    },
    "revives": {
        "statement": "{e1} revives the hobby {e2}.",
        "question": "What hobby does {e1} revive?",
        "relative": "the hobby {e1} revives",
    },
    "trivializes": {
        "statement": "{e1} trivializes the hobby {e2}.",
        "question": "What hobby does {e1} trivialize?",
        "relative": "the hobby {e1} trivializes",
    },

    # ---------- Event ↔ Skill ----------
    "requires_evt_skl": {
        "statement": "{e1} requires the skill {e2}.",
        "question": "What skill does {e1} require?",
        "relative": "the skill {e1} requires",
    },
    "teaches_evt_skl": {
        "statement": "{e1} teaches the skill {e2}.",
        "question": "What skill does {e1} teach?",
        "relative": "the skill {e1} teaches",
    },
    "tests_evt_skl": {
        "statement": "{e1} tests the skill {e2}.",
        "question": "What skill does {e1} test?",
        "relative": "the skill {e1} tests",
    },
    "showcases_evt_skl": {
        "statement": "{e1} showcases the skill {e2}.",
        "question": "What skill does {e1} showcase?",
        "relative": "the skill {e1} showcases",
    },
    "certifies_evt_skl": {
        "statement": "{e1} certifies the skill {e2}.",
        "question": "What skill does {e1} certify?",
        "relative": "the skill {e1} certifies",
    },
    "develops_evt_skl": {
        "statement": "{e1} develops the skill {e2}.",
        "question": "What skill does {e1} develop?",
        "relative": "the skill {e1} develops",
    },
    "rewards": {
        "statement": "{e1} rewards the skill {e2}.",
        "question": "What skill does {e1} reward?",
        "relative": "the skill {e1} rewards",
    },
    "undervalues_evt_skl": {
        "statement": "{e1} undervalues the skill {e2}.",
        "question": "What skill does {e1} undervalue?",
        "relative": "the skill {e1} undervalues",
    },
    "highlights": {
        "statement": "{e1} highlights the skill {e2}.",
        "question": "What skill does {e1} highlight?",
        "relative": "the skill {e1} highlights",
    },
    "debates_evt_skl": {
        "statement": "{e1} debates the skill {e2}.",
        "question": "What skill does {e1} debate?",
        "relative": "the skill {e1} debates",
    },

    # ---------- Event ↔ PhysicalObject ----------
    "features": {
        "statement": "{e1} features the object {e2}.",
        "question": "What object does {e1} feature?",
        "relative": "the object {e1} features",
    },
    "damages": {
        "statement": "{e1} damages the object {e2}.",
        "question": "What object does {e1} damage?",
        "relative": "the object {e1} damages",
    },
    "displays_evt_obj": {
        "statement": "{e1} displays the object {e2}.",
        "question": "What object does {e1} display?",
        "relative": "the object {e1} displays",
    },
    "auctions_evt_obj": {
        "statement": "{e1} auctions the object {e2}.",
        "question": "What object does {e1} auction?",
        "relative": "the object {e1} auctions",
    },
    "distributes_evt_obj": {
        "statement": "{e1} distributes the object {e2}.",
        "question": "What object does {e1} distribute?",
        "relative": "the object {e1} distributes",
    },
    "requires_evt_obj": {
        "statement": "{e1} requires the object {e2}.",
        "question": "What object does {e1} require?",
        "relative": "the object {e1} requires",
    },
    "commemorates": {
        "statement": "{e1} commemorates the object {e2}.",
        "question": "What object does {e1} commemorate?",
        "relative": "the object {e1} commemorates",
    },
    "destroys": {
        "statement": "{e1} destroys the object {e2}.",
        "question": "What object does {e1} destroy?",
        "relative": "the object {e1} destroys",
    },
    "unveils": {
        "statement": "{e1} unveils the object {e2}.",
        "question": "What object does {e1} unveil?",
        "relative": "the object {e1} unveils",
    },
    "bans_evt_obj": {
        "statement": "{e1} bans the object {e2}.",
        "question": "What object does {e1} ban?",
        "relative": "the object {e1} bans",
    },

    # ---------- Event ↔ Product ----------
    "launches": {
        "statement": "{e1} launches the product {e2}.",
        "question": "What product does {e1} launch?",
        "relative": "the product {e1} launches",
    },
    "recalls_evt_prd": {
        "statement": "{e1} recalls the product {e2}.",
        "question": "What product does {e1} recall?",
        "relative": "the product {e1} recalls",
    },
    "showcases_evt_prd": {
        "statement": "{e1} showcases the product {e2}.",
        "question": "What product does {e1} showcase?",
        "relative": "the product {e1} showcases",
    },
    "reviews_evt_prd": {
        "statement": "{e1} reviews the product {e2}.",
        "question": "What product does {e1} review?",
        "relative": "the product {e1} reviews",
    },
    "awards_evt_prd": {
        "statement": "{e1} awards the product {e2}.",
        "question": "What product does {e1} award?",
        "relative": "the product {e1} awards",
    },
    "promotes_evt_prd": {
        "statement": "{e1} promotes the product {e2}.",
        "question": "What product does {e1} promote?",
        "relative": "the product {e1} promotes",
    },
    "discounts": {
        "statement": "{e1} discounts the product {e2}.",
        "question": "What product does {e1} discount?",
        "relative": "the product {e1} discounts",
    },
    "bans_evt_prd": {
        "statement": "{e1} bans the product {e2}.",
        "question": "What product does {e1} ban?",
        "relative": "the product {e1} bans",
    },
    "tests_evt_prd": {
        "statement": "{e1} tests the product {e2}.",
        "question": "What product does {e1} test?",
        "relative": "the product {e1} tests",
    },
    "announces": {
        "statement": "{e1} announces the product {e2}.",
        "question": "What product does {e1} announce?",
        "relative": "the product {e1} announces",
    },

    # ---------- Event ↔ Service ----------
    "debuts": {
        "statement": "{e1} debuts the service {e2}.",
        "question": "What service does {e1} debut?",
        "relative": "the service {e1} debuts",
    },
    "disrupts_evt_svc": {
        "statement": "{e1} disrupts the service {e2}.",
        "question": "What service does {e1} disrupt?",
        "relative": "the service {e1} disrupts",
    },
    "promotes_evt_svc": {
        "statement": "{e1} promotes the service {e2}.",
        "question": "What service does {e1} promote?",
        "relative": "the service {e1} promotes",
    },
    "requires_evt_svc": {
        "statement": "{e1} requires the service {e2}.",
        "question": "What service does {e1} require?",
        "relative": "the service {e1} requires",
    },
    "reviews_evt_svc": {
        "statement": "{e1} reviews the service {e2}.",
        "question": "What service does {e1} review?",
        "relative": "the service {e1} reviews",
    },
    "showcases_evt_svc": {
        "statement": "{e1} showcases the service {e2}.",
        "question": "What service does {e1} showcase?",
        "relative": "the service {e1} showcases",
    },
    "subsidizes_evt_svc": {
        "statement": "{e1} subsidizes the service {e2}.",
        "question": "What service does {e1} subsidize?",
        "relative": "the service {e1} subsidizes",
    },
    "bans_evt_svc": {
        "statement": "{e1} bans the service {e2}.",
        "question": "What service does {e1} ban?",
        "relative": "the service {e1} bans",
    },
    "tests_evt_svc": {
        "statement": "{e1} tests the service {e2}.",
        "question": "What service does {e1} test?",
        "relative": "the service {e1} tests",
    },
    "announces_evt_svc": {
        "statement": "{e1} announces the service {e2}.",
        "question": "What service does {e1} announce?",
        "relative": "the service {e1} announces",
    },

    # ---------- Event ↔ MediaWork ----------
    "premieres": {
        "statement": "{e1} premieres the media work {e2}.",
        "question": "What media work does {e1} premiere?",
        "relative": "the media work {e1} premieres",
    },
    "inspires": {
        "statement": "{e1} inspires the media work {e2}.",
        "question": "What media work does {e1} inspire?",
        "relative": "the media work {e1} inspires",
    },
    "awards_evt_mda": {
        "statement": "{e1} awards the media work {e2}.",
        "question": "What media work does {e1} award?",
        "relative": "the media work {e1} awards",
    },
    "screens": {
        "statement": "{e1} screens the media work {e2}.",
        "question": "What media work does {e1} screen?",
        "relative": "the media work {e1} screens",
    },
    "reviews_evt_mda": {
        "statement": "{e1} reviews the media work {e2}.",
        "question": "What media work does {e1} review?",
        "relative": "the media work {e1} reviews",
    },
    "bans_evt_mda": {
        "statement": "{e1} bans the media work {e2}.",
        "question": "What media work does {e1} ban?",
        "relative": "the media work {e1} bans",
    },
    "celebrates_evt_mda": {
        "statement": "{e1} celebrates the media work {e2}.",
        "question": "What media work does {e1} celebrate?",
        "relative": "the media work {e1} celebrates",
    },
    "adapts_evt_mda": {
        "statement": "{e1} adapts the media work {e2}.",
        "question": "What media work does {e1} adapt?",
        "relative": "the media work {e1} adapts",
    },
    "is_documented_in_evt_mda": {
        "statement": "{e1} is documented in the media work {e2}.",
        "question": "What media work documents {e1}?",
        "relative": "the media work that documents {e1}",
    },
    "promotes_evt_mda": {
        "statement": "{e1} promotes the media work {e2}.",
        "question": "What media work does {e1} promote?",
        "relative": "the media work {e1} promotes",
    },

    # ---------- Event ↔ DigitalTool ----------
    "utilizes": {
        "statement": "{e1} utilizes the digital tool {e2}.",
        "question": "What digital tool does {e1} utilize?",
        "relative": "the digital tool {e1} utilizes",
    },
    "debuts_evt_dgt": {
        "statement": "{e1} debuts the digital tool {e2}.",
        "question": "What digital tool does {e1} debut?",
        "relative": "the digital tool {e1} debuts",
    },
    "showcases_evt_dgt": {
        "statement": "{e1} showcases the digital tool {e2}.",
        "question": "What digital tool does {e1} showcase?",
        "relative": "the digital tool {e1} showcases",
    },
    "requires_evt_dgt": {
        "statement": "{e1} requires the digital tool {e2}.",
        "question": "What digital tool does {e1} require?",
        "relative": "the digital tool {e1} requires",
    },
    "is_streamed_via": {
        "statement": "{e1} is streamed via the digital tool {e2}.",
        "question": "What digital tool is {e1} streamed via?",
        "relative": "the digital tool {e1} is streamed via",
    },
    "promotes_evt_dgt": {
        "statement": "{e1} promotes the digital tool {e2}.",
        "question": "What digital tool does {e1} promote?",
        "relative": "the digital tool {e1} promotes",
    },
    "tests_evt_dgt": {
        "statement": "{e1} tests the digital tool {e2}.",
        "question": "What digital tool does {e1} test?",
        "relative": "the digital tool {e1} tests",
    },
    "is_disrupted_by": {
        "statement": "{e1} is disrupted by the digital tool {e2}.",
        "question": "What digital tool disrupts {e1}?",
        "relative": "the digital tool that disrupts {e1}",
    },
    "awards_evt_dgt": {
        "statement": "{e1} awards the digital tool {e2}.",
        "question": "What digital tool does {e1} award?",
        "relative": "the digital tool {e1} awards",
    },
    "bans_evt_dgt": {
        "statement": "{e1} bans the digital tool {e2}.",
        "question": "What digital tool does {e1} ban?",
        "relative": "the digital tool {e1} bans",
    },

    # ---------- Event ↔ Task ----------
    "initiates": {
        "statement": "{e1} initiates the task {e2}.",
        "question": "What task does {e1} initiate?",
        "relative": "the task {e1} initiates",
    },
    "concludes": {
        "statement": "{e1} concludes the task {e2}.",
        "question": "What task does {e1} conclude?",
        "relative": "the task {e1} concludes",
    },
    "requires_evt_tsk": {
        "statement": "{e1} requires the task {e2}.",
        "question": "What task does {e1} require?",
        "relative": "the task {e1} requires",
    },
    "automates_evt_tsk": {
        "statement": "{e1} automates the task {e2}.",
        "question": "What task does {e1} automate?",
        "relative": "the task {e1} automates",
    },
    "delays_evt_tsk": {
        "statement": "{e1} delays the task {e2}.",
        "question": "What task does {e1} delay?",
        "relative": "the task {e1} delays",
    },
    "prioritizes_evt_tsk": {
        "statement": "{e1} prioritizes the task {e2}.",
        "question": "What task does {e1} prioritize?",
        "relative": "the task {e1} prioritizes",
    },
    "assigns_evt_tsk": {
        "statement": "{e1} assigns the task {e2}.",
        "question": "What task does {e1} assign?",
        "relative": "the task {e1} assigns",
    },
    "celebrates_completion_of": {
        "statement": "{e1} celebrates completion of the task {e2}.",
        "question": "What task completion does {e1} celebrate?",
        "relative": "the task that completion does {e1} celebrate",
    },
    "disrupts_evt_tsk": {
        "statement": "{e1} disrupts the task {e2}.",
        "question": "What task does {e1} disrupt?",
        "relative": "the task {e1} disrupts",
    },
    "schedules": {
        "statement": "{e1} schedules the task {e2}.",
        "question": "What task does {e1} schedule?",
        "relative": "the task {e1} schedules",
    },

    # ---------- Event ↔ TimePeriod ----------
    "occurs_in": {
        "statement": "{e1} occurs in the time period {e2}.",
        "question": "What time period does {e1} occur in?",
        "relative": "the time period {e1} occurs in",
    },
    "spans": {
        "statement": "{e1} spans the time period {e2}.",
        "question": "What time period does {e1} span?",
        "relative": "the time period {e1} spans",
    },
    "defines": {
        "statement": "{e1} defines the time period {e2}.",
        "question": "What time period does {e1} define?",
        "relative": "the time period {e1} defines",
    },
    "concludes_evt_tmp": {
        "statement": "{e1} concludes the time period {e2}.",
        "question": "What time period does {e1} conclude?",
        "relative": "the time period {e1} concludes",
    },
    "begins": {
        "statement": "{e1} begins the time period {e2}.",
        "question": "What time period does {e1} begin?",
        "relative": "the time period {e1} begins",
    },
    "recurs_during": {
        "statement": "{e1} recurs during the time period {e2}.",
        "question": "What time period does {e1} recur during?",
        "relative": "the time period {e1} recurs during",
    },
    "is_commemorated_in": {
        "statement": "{e1} is commemorated in the time period {e2}.",
        "question": "What time period is {e1} commemorated in?",
        "relative": "the time period {e1} is commemorated in",
    },
    "was_postponed_to": {
        "statement": "{e1} was postponed to the time period {e2}.",
        "question": "What time period was {e1} postponed to?",
        "relative": "the time period {e1} was postponed to",
    },
    "was_cancelled_in": {
        "statement": "{e1} was cancelled in the time period {e2}.",
        "question": "What time period was {e1} cancelled in?",
        "relative": "the time period {e1} was cancelled in",
    },
    "transformed": {
        "statement": "{e1} transformed the time period {e2}.",
        "question": "What time period did {e1} transform?",
        "relative": "the time period {e1} transformed",
    },

    # ---------- Profession ↔ Hobby ----------
    "evolves_from": {
        "statement": "{e1} evolves from the hobby {e2}.",
        "question": "What hobby does {e1} evolve from?",
        "relative": "the hobby {e1} evolves from",
    },
    "is_complemented_by": {
        "statement": "{e1} is complemented by the hobby {e2}.",
        "question": "What hobby complements {e1}?",
        "relative": "the hobby that complements {e1}",
    },
    "monetizes_pro_hob": {
        "statement": "{e1} monetizes the hobby {e2}.",
        "question": "What hobby does {e1} monetize?",
        "relative": "the hobby {e1} monetizes",
    },
    "discourages_pro_hob": {
        "statement": "{e1} discourages the hobby {e2}.",
        "question": "What hobby does {e1} discourage?",
        "relative": "the hobby {e1} discourages",
    },
    "requires_pro_hob": {
        "statement": "{e1} requires the hobby {e2}.",
        "question": "What hobby does {e1} require?",
        "relative": "the hobby {e1} requires",
    },
    "inspires_pro_hob": {
        "statement": "{e1} inspires the hobby {e2}.",
        "question": "What hobby does {e1} inspire?",
        "relative": "the hobby {e1} inspires",
    },
    "overlaps_with": {
        "statement": "{e1} overlaps with the hobby {e2}.",
        "question": "What hobby does {e1} overlap with?",
        "relative": "the hobby {e1} overlaps with",
    },
    "is_distracted_by": {
        "statement": "{e1} is distracted by the hobby {e2}.",
        "question": "What hobby distracts {e1}?",
        "relative": "the hobby that distracts {e1}",
    },
    "benefits_from": {
        "statement": "{e1} benefits from the hobby {e2}.",
        "question": "What hobby does {e1} benefit from?",
        "relative": "the hobby {e1} benefits from",
    },
    "is_gateway_to": {
        "statement": "{e1} is a gateway to the hobby {e2}.",
        "question": "What hobby is {e1} a gateway to?",
        "relative": "the hobby {e1} is a gateway to",
    },

    # ---------- Profession ↔ Skill ----------
    "requires_pro_skl": {
        "statement": "{e1} requires the skill {e2}.",
        "question": "What skill does {e1} require?",
        "relative": "the skill {e1} requires",
    },
    "develops_pro_skl": {
        "statement": "{e1} develops the skill {e2}.",
        "question": "What skill does {e1} develop?",
        "relative": "the skill {e1} develops",
    },
    "certifies_pro_skl": {
        "statement": "{e1} certifies the skill {e2}.",
        "question": "What skill does {e1} certify?",
        "relative": "the skill {e1} certifies",
    },
    "values_pro_skl": {
        "statement": "{e1} values the skill {e2}.",
        "question": "What skill does {e1} value?",
        "relative": "the skill {e1} values",
    },
    "teaches_pro_skl": {
        "statement": "{e1} teaches the skill {e2}.",
        "question": "What skill does {e1} teach?",
        "relative": "the skill {e1} teaches",
    },
    "automates_pro_skl": {
        "statement": "{e1} automates the skill {e2}.",
        "question": "What skill does {e1} automate?",
        "relative": "the skill {e1} automates",
    },
    "undervalues_pro_skl": {
        "statement": "{e1} undervalues the skill {e2}.",
        "question": "What skill does {e1} undervalue?",
        "relative": "the skill {e1} undervalues",
    },
    "is_defined_by": {
        "statement": "{e1} is defined by the skill {e2}.",
        "question": "What skill defines {e1}?",
        "relative": "the skill that defines {e1}",
    },
    "benchmarks_pro_skl": {
        "statement": "{e1} benchmarks the skill {e2}.",
        "question": "What skill does {e1} benchmark?",
        "relative": "the skill {e1} benchmarks",
    },
    "is_disrupted_by_pro_skl": {
        "statement": "{e1} is disrupted by the skill {e2}.",
        "question": "What skill disrupts {e1}?",
        "relative": "the skill that disrupts {e1}",
    },

    # ---------- Profession ↔ PhysicalObject ----------
    "utilizes_pro_obj": {
        "statement": "{e1} utilizes the object {e2}.",
        "question": "What object does {e1} utilize?",
        "relative": "the object {e1} utilizes",
    },
    "requires_pro_obj": {
        "statement": "{e1} requires the object {e2}.",
        "question": "What object does {e1} require?",
        "relative": "the object {e1} requires",
    },
    "repairs_pro_obj": {
        "statement": "{e1} repairs the object {e2}.",
        "question": "What object does {e1} repair?",
        "relative": "the object {e1} repairs",
    },
    "manufactures_pro_obj": {
        "statement": "{e1} manufactures the object {e2}.",
        "question": "What object does {e1} manufacture?",
        "relative": "the object {e1} manufactures",
    },
    "is_defined_by_pro_obj": {
        "statement": "{e1} is defined by the object {e2}.",
        "question": "What object defines {e1}?",
        "relative": "the object that defines {e1}",
    },

    "maintains": {
        "statement": "{e1} maintains the object {e2}.",
        "question": "What object does {e1} maintain?",
        "relative": "the object {e1} maintains",
    },
    "designs": {
        "statement": "{e1} designs the object {e2}.",
        "question": "What object does {e1} design?",
        "relative": "the object {e1} designs",
    },
    "is_endangered_by": {
        "statement": "{e1} is endangered by the object {e2}.",
        "question": "What object is {e1} endangered by?",
        "relative": "the object {e1} is endangered by",
    },
    "calibrates": {
        "statement": "{e1} calibrates the object {e2}.",
        "question": "What object does {e1} calibrate?",
        "relative": "the object {e1} calibrates",
    },
    "disposes_of": {
        "statement": "{e1} disposes of the object {e2}.",
        "question": "What object does {e1} dispose of?",
        "relative": "the object {e1} disposes of",
    },
    # ---------- Profession ↔ Product ----------
    "creates_pro_prd": {
        "statement": "{e1} creates the product {e2}.",
        "question": "What product does {e1} create?",
        "relative": "the product {e1} creates",
    },
    "consumes_pro_prd": {
        "statement": "{e1} consumes the product {e2}.",
        "question": "What product does {e1} consume?",
        "relative": "the product {e1} consumes",
    },
    "reviews_pro_prd": {
        "statement": "{e1} reviews the product {e2}.",
        "question": "What product does {e1} review?",
        "relative": "the product {e1} reviews",
    },
    "recommends_pro_prd": {
        "statement": "{e1} recommends the product {e2}.",
        "question": "What product does {e1} recommend?",
        "relative": "the product {e1} recommends",
    },
    "regulates_pro_prd": {
        "statement": "{e1} regulates the product {e2}.",
        "question": "What product does {e1} regulate?",
        "relative": "the product {e1} regulates",
    },
    "is_disrupted_by_pro_prd": {
        "statement": "{e1} is disrupted by the product {e2}.",
        "question": "What product disrupts {e1}?",
        "relative": "the product that disrupts {e1}",
    },
    "markets_pro_prd": {
        "statement": "{e1} markets the product {e2}.",
        "question": "What product does {e1} market?",
        "relative": "the product {e1} markets",
    },
    "tests_pro_prd": {
        "statement": "{e1} tests the product {e2}.",
        "question": "What product does {e1} test?",
        "relative": "the product {e1} tests",
    },
    "is_dependent_on_pro_prd": {
        "statement": "{e1} is dependent on the product {e2}.",
        "question": "What product is {e1} dependent on?",
        "relative": "the product {e1} is dependent on",
    },
    "certifies_pro_prd": {
        "statement": "{e1} certifies the product {e2}.",
        "question": "What product does {e1} certify?",
        "relative": "the product {e1} certifies",
    },

    # ---------- Profession ↔ Service ----------
    "relies_on_pro_svc": {
        "statement": "{e1} relies on the service {e2}.",
        "question": "What service does {e1} rely on?",
        "relative": "the service {e1} relies on",
    },
    "regulates_pro_svc": {
        "statement": "{e1} regulates the service {e2}.",
        "question": "What service does {e1} regulate?",
        "relative": "the service {e1} regulates",
    },
    "designs_pro_svc": {
        "statement": "{e1} designs the service {e2}.",
        "question": "What service does {e1} design?",
        "relative": "the service {e1} designs",
    },
    "audits_pro_svc": {
        "statement": "{e1} audits the service {e2}.",
        "question": "What service does {e1} audit?",
        "relative": "the service {e1} audits",
    },
    "markets_pro_svc": {
        "statement": "{e1} markets the service {e2}.",
        "question": "What service does {e1} market?",
        "relative": "the service {e1} markets",
    },
    "is_dependent_on_pro_svc": {
        "statement": "{e1} is dependent on the service {e2}.",
        "question": "What service is {e1} dependent on?",
        "relative": "the service {e1} is dependent on",
    },
    "certifies_pro_svc": {
        "statement": "{e1} certifies the service {e2}.",
        "question": "What service does {e1} certify?",
        "relative": "the service {e1} certifies",
    },

    "delivers": {
        "statement": "{e1} delivers the service {e2}.",
        "question": "What service does {e1} deliver?",
        "relative": "the service {e1} delivers",
    },
    "is_replaced_by": {
        "statement": "{e1} is replaced by the service {e2}.",
        "question": "What service is {e1} replaced by?",
        "relative": "the service {e1} is replaced by",
    },
    "improves": {
        "statement": "{e1} improves the service {e2}.",
        "question": "What service does {e1} improve?",
        "relative": "the service {e1} improves",
    },
    # ---------- Profession ↔ MediaWork ----------
    "produces_pro_mda": {
        "statement": "{e1} produces the media work {e2}.",
        "question": "What media work does {e1} produce?",
        "relative": "the media work {e1} produces",
    },
    "reviews_pro_mda": {
        "statement": "{e1} reviews the media work {e2}.",
        "question": "What media work does {e1} review?",
        "relative": "the media work {e1} reviews",
    },
    "creates_pro_mda": {
        "statement": "{e1} creates the media work {e2}.",
        "question": "What media work does {e1} create?",
        "relative": "the media work {e1} creates",
    },
    "archives_pro_mda": {
        "statement": "{e1} archives the media work {e2}.",
        "question": "What media work does {e1} archive?",
        "relative": "the media work {e1} archives",
    },
    "is_misrepresented_in_pro_mda": {
        "statement": "{e1} is misrepresented in the media work {e2}.",
        "question": "What media work misrepresents {e1}?",
        "relative": "the media work that misrepresents {e1}",
    },

    "is_depicted_in": {
        "statement": "{e1} is depicted in the media work {e2}.",
        "question": "What media work is {e1} depicted in?",
        "relative": "the media work {e1} is depicted in",
    },
    "is_celebrated_in": {
        "statement": "{e1} is celebrated in the media work {e2}.",
        "question": "What media work is {e1} celebrated in?",
        "relative": "the media work {e1} is celebrated in",
    },
    "is_satirized_in": {
        "statement": "{e1} is satirized in the media work {e2}.",
        "question": "What media work is {e1} satirized in?",
        "relative": "the media work {e1} is satirized in",
    },
    "is_trained_by": {
        "statement": "{e1} is trained by the media work {e2}.",
        "question": "What media work is {e1} trained by?",
        "relative": "the media work {e1} is trained by",
    },
    "curates": {
        "statement": "{e1} curates the media work {e2}.",
        "question": "What media work does {e1} curate?",
        "relative": "the media work {e1} curates",
    },
    # ---------- Profession ↔ DigitalTool ----------
    "is_replaced_by_pro_dgt": {
        "statement": "{e1} is replaced by the digital tool {e2}.",
        "question": "What digital tool is {e1} replaced by?",
        "relative": "the digital tool {e1} is replaced by",
    },
    "develops_pro_dgt": {
        "statement": "{e1} develops the digital tool {e2}.",
        "question": "What digital tool does {e1} develop?",
        "relative": "the digital tool {e1} develops",
    },
    "relies_on_pro_dgt": {
        "statement": "{e1} relies on the digital tool {e2}.",
        "question": "What digital tool does {e1} rely on?",
        "relative": "the digital tool {e1} relies on",
    },
    "certifies_pro_dgt": {
        "statement": "{e1} certifies the digital tool {e2}.",
        "question": "What digital tool does {e1} certify?",
        "relative": "the digital tool {e1} certifies",
    },
    "customizes_pro_dgt": {
        "statement": "{e1} customizes the digital tool {e2}.",
        "question": "What digital tool does {e1} customize?",
        "relative": "the digital tool {e1} customizes",
    },
    "is_disrupted_by_pro_dgt": {
        "statement": "{e1} is disrupted by the digital tool {e2}.",
        "question": "What digital tool disrupts {e1}?",
        "relative": "the digital tool that disrupts {e1}",
    },
    "audits_pro_dgt": {
        "statement": "{e1} audits the digital tool {e2}.",
        "question": "What digital tool does {e1} audit?",
        "relative": "the digital tool {e1} audits",
    },
    "teaches_pro_dgt": {
        "statement": "{e1} teaches the digital tool {e2}.",
        "question": "What digital tool does {e1} teach?",
        "relative": "the digital tool {e1} teaches",
    },

    "operates": {
        "statement": "{e1} operates the digital tool {e2}.",
        "question": "What digital tool does {e1} operate?",
        "relative": "the digital tool {e1} operates",
    },
    "is_augmented_by": {
        "statement": "{e1} is augmented by the digital tool {e2}.",
        "question": "What digital tool is {e1} augmented by?",
        "relative": "the digital tool {e1} is augmented by",
    },
    # ---------- Profession ↔ Task ----------
    "avoids_pro_tsk": {
        "statement": "{e1} avoids the task {e2}.",
        "question": "What task does {e1} avoid?",
        "relative": "the task {e1} avoids",
    },
    "automates_pro_tsk": {
        "statement": "{e1} automates the task {e2}.",
        "question": "What task does {e1} automate?",
        "relative": "the task {e1} automates",
    },
    "delegates_pro_tsk": {
        "statement": "{e1} delegates the task {e2}.",
        "question": "What task does {e1} delegate?",
        "relative": "the task {e1} delegates",
    },
    "is_defined_by_pro_tsk": {
        "statement": "{e1} is defined by the task {e2}.",
        "question": "What task defines {e1}?",
        "relative": "the task that defines {e1}",
    },
    "standardizes_pro_tsk": {
        "statement": "{e1} standardizes the task {e2}.",
        "question": "What task does {e1} standardize?",
        "relative": "the task {e1} standardizes",
    },
    "is_overwhelmed_by_pro_tsk": {
        "statement": "{e1} is overwhelmed by the task {e2}.",
        "question": "What task overwhelms {e1}?",
        "relative": "the task that overwhelms {e1}",
    },
    "documents_pro_tsk": {
        "statement": "{e1} documents the task {e2}.",
        "question": "What task does {e1} document?",
        "relative": "the task {e1} documents",
    },

    "specializes_in": {
        "statement": "{e1} specializes in the task {e2}.",
        "question": "What task does {e1} specialize in?",
        "relative": "the task {e1} specializes in",
    },
    "trains_for": {
        "statement": "{e1} trains for the task {e2}.",
        "question": "What task does {e1} train for?",
        "relative": "the task {e1} trains for",
    },
    "is_evaluated_by": {
        "statement": "{e1} is evaluated by the task {e2}.",
        "question": "What task is {e1} evaluated by?",
        "relative": "the task {e1} is evaluated by",
    },
    # ---------- Profession ↔ TimePeriod ----------
    "flourished_during_pro_tmp": {
        "statement": "{e1} flourished during the time period {e2}.",
        "question": "What time period did {e1} flourish during?",
        "relative": "the time period {e1} flourished during",
    },
    "peaked_during_pro_tmp": {
        "statement": "{e1} peaked during the time period {e2}.",
        "question": "What time period did {e1} peak during?",
        "relative": "the time period {e1} peaked during",
    },
    "declined_during_pro_tmp": {
        "statement": "{e1} declined during the time period {e2}.",
        "question": "What time period did {e1} decline during?",
        "relative": "the time period {e1} declined during",
    },

    "emerged_in": {
        "statement": "{e1} emerged in the time period {e2}.",
        "question": "What time period did {e1} emerge in?",
        "relative": "the time period {e1} emerged in",
    },
    "became_obsolete_by": {
        "statement": "{e1} became obsolete by the time period {e2}.",
        "question": "What time period did {e1} become obsolete by?",
        "relative": "the time period {e1} became obsolete by",
    },
    "was_regulated_in": {
        "statement": "{e1} was regulated in the time period {e2}.",
        "question": "What time period was {e1} regulated in?",
        "relative": "the time period {e1} was regulated in",
    },
    "was_automated_in": {
        "statement": "{e1} was automated in the time period {e2}.",
        "question": "What time period was {e1} automated in?",
        "relative": "the time period {e1} was automated in",
    },
    "was_unionized_in": {
        "statement": "{e1} was unionized in the time period {e2}.",
        "question": "What time period was {e1} unionized in?",
        "relative": "the time period {e1} was unionized in",
    },
    "was_professionalized_in": {
        "statement": "{e1} was professionalized in the time period {e2}.",
        "question": "What time period was {e1} professionalized in?",
        "relative": "the time period {e1} was professionalized in",
    },
    "was_disrupted_in": {
        "statement": "{e1} was disrupted in the time period {e2}.",
        "question": "What time period was {e1} disrupted in?",
        "relative": "the time period {e1} was disrupted in",
    },
    # ---------- Hobby ↔ Skill ----------
    "develops_hob_skl": {
        "statement": "{e1} develops the skill {e2}.",
        "question": "What skill does {e1} develop?",
        "relative": "the skill {e1} develops",
    },
    "requires_hob_skl": {
        "statement": "{e1} requires the skill {e2}.",
        "question": "What skill does {e1} require?",
        "relative": "the skill {e1} requires",
    },
    "teaches_hob_skl": {
        "statement": "{e1} teaches the skill {e2}.",
        "question": "What skill does {e1} teach?",
        "relative": "the skill {e1} teaches",
    },
    "is_gateway_to_hob_skl": {
        "statement": "{e1} is a gateway to the skill {e2}.",
        "question": "What skill is {e1} a gateway to?",
        "relative": "the skill {e1} is a gateway to",
    },
    "complements": {
        "statement": "{e1} complements the skill {e2}.",
        "question": "What skill does {e1} complement?",
        "relative": "the skill {e1} complements",
    },

    "refines": {
        "statement": "{e1} refines the skill {e2}.",
        "question": "What skill does {e1} refine?",
        "relative": "the skill {e1} refines",
    },
    "challenges": {
        "statement": "{e1} challenges the skill {e2}.",
        "question": "What skill does {e1} challenge?",
        "relative": "the skill {e1} challenges",
    },
    "is_limited_by": {
        "statement": "{e1} is limited by the skill {e2}.",
        "question": "What skill is {e1} limited by?",
        "relative": "the skill {e1} is limited by",
    },
    "measures": {
        "statement": "{e1} measures the skill {e2}.",
        "question": "What skill does {e1} measure?",
        "relative": "the skill {e1} measures",
    },
    "is_enhanced_by": {
        "statement": "{e1} is enhanced by the skill {e2}.",
        "question": "What skill is {e1} enhanced by?",
        "relative": "the skill {e1} is enhanced by",
    },
    # ---------- Hobby ↔ PhysicalObject ----------
    "utilizes_hob_obj": {
        "statement": "{e1} utilizes the object {e2}.",
        "question": "What object does {e1} utilize?",
        "relative": "the object {e1} utilizes",
    },
    "collects_hob_obj": {
        "statement": "{e1} collects the object {e2}.",
        "question": "What object does {e1} collect?",
        "relative": "the object {e1} collects",
    },
    "requires_hob_obj": {
        "statement": "{e1} requires the object {e2}.",
        "question": "What object does {e1} require?",
        "relative": "the object {e1} requires",
    },
    "produces_hob_obj": {
        "statement": "{e1} produces the object {e2}.",
        "question": "What object does {e1} produce?",
        "relative": "the object {e1} produces",
    },
    "displays_hob_obj": {
        "statement": "{e1} displays the object {e2}.",
        "question": "What object does {e1} display?",
        "relative": "the object {e1} displays",
    },
    "is_defined_by_hob_obj": {
        "statement": "{e1} is defined by the object {e2}.",
        "question": "What object defines {e1}?",
        "relative": "the object that defines {e1}",
    },
    "is_limited_by_hob_obj": {
        "statement": "{e1} is limited by the object {e2}.",
        "question": "What object is {e1} limited by?",
        "relative": "the object {e1} is limited by",
    },

    "restores": {
        "statement": "{e1} restores the object {e2}.",
        "question": "What object does {e1} restore?",
        "relative": "the object {e1} restores",
    },
    "modifies": {
        "statement": "{e1} modifies the object {e2}.",
        "question": "What object does {e1} modify?",
        "relative": "the object {e1} modifies",
    },
    "repurposes": {
        "statement": "{e1} repurposes the object {e2}.",
        "question": "What object does {e1} repurpose?",
        "relative": "the object {e1} repurposes",
    },
    # ---------- Hobby ↔ Product ----------
    "consumes_hob_prd": {
        "statement": "{e1} consumes the product {e2}.",
        "question": "What product does {e1} consume?",
        "relative": "the product {e1} consumes",
    },
    "creates_hob_prd": {
        "statement": "{e1} creates the product {e2}.",
        "question": "What product does {e1} create?",
        "relative": "the product {e1} creates",
    },
    "requires_hob_prd": {
        "statement": "{e1} requires the product {e2}.",
        "question": "What product does {e1} require?",
        "relative": "the product {e1} requires",
    },
    "reviews_hob_prd": {
        "statement": "{e1} reviews the product {e2}.",
        "question": "What product does {e1} review?",
        "relative": "the product {e1} reviews",
    },
    "is_enhanced_by_hob_prd": {
        "statement": "{e1} is enhanced by the product {e2}.",
        "question": "What product is {e1} enhanced by?",
        "relative": "the product {e1} is enhanced by",
    },
    "repurposes_hob_prd": {
        "statement": "{e1} repurposes the product {e2}.",
        "question": "What product does {e1} repurpose?",
        "relative": "the product {e1} repurposes",
    },
    "is_limited_by_hob_prd": {
        "statement": "{e1} is limited by the product {e2}.",
        "question": "What product is {e1} limited by?",
        "relative": "the product {e1} is limited by",
    },

    "is_monetized_by": {
        "statement": "{e1} is monetized by the product {e2}.",
        "question": "What product is {e1} monetized by?",
        "relative": "the product {e1} is monetized by",
    },
    "drives_demand_for": {
        "statement": "{e1} drives demand for the product {e2}.",
        "question": "What product does {e1} drive demand for?",
        "relative": "the product {e1} drives demand for",
    },
    "is_trivialized_by": {
        "statement": "{e1} is trivialized by the product {e2}.",
        "question": "What product is {e1} trivialized by?",
        "relative": "the product {e1} is trivialized by",
    },
    # ---------- Hobby ↔ Service ----------
    "utilizes_hob_svc": {
        "statement": "{e1} utilizes the service {e2}.",
        "question": "What service does {e1} utilize?",
        "relative": "the service {e1} utilizes",
    },
    "inspires_hob_svc": {
        "statement": "{e1} inspires the service {e2}.",
        "question": "What service does {e1} inspire?",
        "relative": "the service {e1} inspires",
    },
    "requires_hob_svc": {
        "statement": "{e1} requires the service {e2}.",
        "question": "What service does {e1} require?",
        "relative": "the service {e1} requires",
    },
    "drives_demand_for_hob_svc": {
        "statement": "{e1} drives demand for the service {e2}.",
        "question": "What service does {e1} drive demand for?",
        "relative": "the service {e1} drives demand for",
    },
    "is_monetized_by_hob_svc": {
        "statement": "{e1} is monetized by the service {e2}.",
        "question": "What service is {e1} monetized by?",
        "relative": "the service {e1} is monetized by",
    },
    "benefits_from_hob_svc": {
        "statement": "{e1} benefits from the service {e2}.",
        "question": "What service does {e1} benefit from?",
        "relative": "the service {e1} benefits from",
    },
    "is_regulated_by_hob_svc": {
        "statement": "{e1} is regulated by the service {e2}.",
        "question": "What service regulates {e1}?",
        "relative": "the service that regulates {e1}",
    },
    "is_enhanced_by_hob_svc": {
        "statement": "{e1} is enhanced by the service {e2}.",
        "question": "What service is {e1} enhanced by?",
        "relative": "the service {e1} is enhanced by",
    },

    "is_supported_by": {
        "statement": "{e1} is supported by the service {e2}.",
        "question": "What service is {e1} supported by?",
        "relative": "the service {e1} is supported by",
    },
    "is_taught_by": {
        "statement": "{e1} is taught by the service {e2}.",
        "question": "What service is {e1} taught by?",
        "relative": "the service {e1} is taught by",
    },
    # ---------- Hobby ↔ MediaWork ----------
    "is_inspired_by_hob_mda": {
        "statement": "{e1} is inspired by the media work {e2}.",
        "question": "What media work inspires {e1}?",
        "relative": "the media work that inspires {e1}",
    },
    "produces_hob_mda": {
        "statement": "{e1} produces the media work {e2}.",
        "question": "What media work does {e1} produce?",
        "relative": "the media work {e1} produces",
    },
    "is_featured_in_hob_mda": {
        "statement": "{e1} is featured in the media work {e2}.",
        "question": "What media work is {e1} featured in?",
        "relative": "the media work {e1} is featured in",
    },
    "is_documented_in_hob_mda": {
        "statement": "{e1} is documented in the media work {e2}.",
        "question": "What media work documents {e1}?",
        "relative": "the media work that documents {e1}",
    },
    "is_celebrated_in_hob_mda": {
        "statement": "{e1} is celebrated in the media work {e2}.",
        "question": "What media work is {e1} celebrated in?",
        "relative": "the media work {e1} is celebrated in",
    },
    "is_taught_by_hob_mda": {
        "statement": "{e1} is taught by the media work {e2}.",
        "question": "What media work is {e1} taught by?",
        "relative": "the media work {e1} is taught by",
    },
    "consumes_hob_mda": {
        "statement": "{e1} consumes the media work {e2}.",
        "question": "What media work does {e1} consume?",
        "relative": "the media work {e1} consumes",
    },
    "is_satirized_in_hob_mda": {
        "statement": "{e1} is satirized in the media work {e2}.",
        "question": "What media work is {e1} satirized in?",
        "relative": "the media work {e1} is satirized in",
    },

    "is_trivialized_in": {
        "statement": "{e1} is trivialized in the media work {e2}.",
        "question": "What media work is {e1} trivialized in?",
        "relative": "the media work {e1} is trivialized in",
    },
    "creates_community_around": {
        "statement": "{e1} creates community around the media work {e2}.",
        "question": "What media work does {e1} create community around?",
        "relative": "the media work {e1} creates community around",
    },
    # ---------- Hobby ↔ DigitalTool ----------
    "is_enhanced_by_hob_dgt": {
        "statement": "{e1} is enhanced by the digital tool {e2}.",
        "question": "What digital tool is {e1} enhanced by?",
        "relative": "the digital tool {e1} is enhanced by",
    },
    "requires_hob_dgt": {
        "statement": "{e1} requires the digital tool {e2}.",
        "question": "What digital tool does {e1} require?",
        "relative": "the digital tool {e1} requires",
    },
    "is_taught_by_hob_dgt": {
        "statement": "{e1} is taught by the digital tool {e2}.",
        "question": "What digital tool is {e1} taught by?",
        "relative": "the digital tool {e1} is taught by",
    },
    "is_monetized_by_hob_dgt": {
        "statement": "{e1} is monetized by the digital tool {e2}.",
        "question": "What digital tool is {e1} monetized by?",
        "relative": "the digital tool {e1} is monetized by",
    },
    "is_disrupted_by_hob_dgt": {
        "statement": "{e1} is disrupted by the digital tool {e2}.",
        "question": "What digital tool disrupts {e1}?",
        "relative": "the digital tool that disrupts {e1}",
    },
    "utilizes_hob_dgt": {
        "statement": "{e1} utilizes the digital tool {e2}.",
        "question": "What digital tool does {e1} utilize?",
        "relative": "the digital tool {e1} utilizes",
    },

    "is_tracked_with": {
        "statement": "{e1} is tracked with the digital tool {e2}.",
        "question": "What digital tool is {e1} tracked with?",
        "relative": "the digital tool {e1} is tracked with",
    },
    "is_community_built_around": {
        "statement": "{e1} is community built around the digital tool {e2}.",
        "question": "What digital tool is {e1} community built around?",
        "relative": "the digital tool {e1} is community built around",
    },
    "is_documented_with": {
        "statement": "{e1} is documented with the digital tool {e2}.",
        "question": "What digital tool is {e1} documented with?",
        "relative": "the digital tool {e1} is documented with",
    },
    "is_gamified_by": {
        "statement": "{e1} is gamified by the digital tool {e2}.",
        "question": "What digital tool is {e1} gamified by?",
        "relative": "the digital tool {e1} is gamified by",
    },
    # ---------- Hobby ↔ Task ----------
    "requires_hob_tsk": {
        "statement": "{e1} requires the task {e2}.",
        "question": "What task does {e1} require?",
        "relative": "the task {e1} requires",
    },
    "complicates_hob_tsk": {
        "statement": "{e1} complicates the task {e2}.",
        "question": "What task does {e1} complicate?",
        "relative": "the task {e1} complicates",
    },
    "automates_hob_tsk": {
        "statement": "{e1} automates the task {e2}.",
        "question": "What task does {e1} automate?",
        "relative": "the task {e1} automates",
    },
    "teaches_hob_tsk": {
        "statement": "{e1} teaches the task {e2}.",
        "question": "What task does {e1} teach?",
        "relative": "the task {e1} teaches",
    },
    "is_defined_by_hob_tsk": {
        "statement": "{e1} is defined by the task {e2}.",
        "question": "What task defines {e1}?",
        "relative": "the task that defines {e1}",
    },

    "involves": {
        "statement": "{e1} involves the task {e2}.",
        "question": "What task does {e1} involve?",
        "relative": "the task {e1} involves",
    },
    "motivates": {
        "statement": "{e1} motivates the task {e2}.",
        "question": "What task does {e1} motivate?",
        "relative": "the task {e1} motivates",
    },
    "simplifies": {
        "statement": "{e1} simplifies the task {e2}.",
        "question": "What task does {e1} simplify?",
        "relative": "the task {e1} simplifies",
    },
    "is_measured_by": {
        "statement": "{e1} is measured by the task {e2}.",
        "question": "What task is {e1} measured by?",
        "relative": "the task {e1} is measured by",
    },
    "distracts_from": {
        "statement": "{e1} distracts from the task {e2}.",
        "question": "What task does {e1} distract from?",
        "relative": "the task {e1} distracts from",
    },
    # ---------- Hobby ↔ TimePeriod ----------
    "declined_during_hob_tmp": {
        "statement": "{e1} declined during the time period {e2}.",
        "question": "What time period did {e1} decline during?",
        "relative": "the time period {e1} declined during",
    },
    "thrived_during_hob_tmp": {
        "statement": "{e1} thrived during the time period {e2}.",
        "question": "What time period did {e1} thrive during?",
        "relative": "the time period {e1} thrived during",
    },
    "was_professionalized_in_hob_tmp": {
        "statement": "{e1} was professionalized in the time period {e2}.",
        "question": "What time period was {e1} professionalized in?",
        "relative": "the time period {e1} was professionalized in",
    },

    "peaks_during": {
        "statement": "{e1} peaks during the time period {e2}.",
        "question": "What time period does {e1} peak during?",
        "relative": "the time period {e1} peaks during",
    },
    "originated_in": {
        "statement": "{e1} originated in the time period {e2}.",
        "question": "What time period did {e1} originate in?",
        "relative": "the time period {e1} originated in",
    },
    "was_popularized_in": {
        "statement": "{e1} was popularized in the time period {e2}.",
        "question": "What time period was {e1} popularized in?",
        "relative": "the time period {e1} was popularized in",
    },
    "was_banned_in": {
        "statement": "{e1} was banned in the time period {e2}.",
        "question": "What time period was {e1} banned in?",
        "relative": "the time period {e1} was banned in",
    },
    "was_commercialized_in": {
        "statement": "{e1} was commercialized in the time period {e2}.",
        "question": "What time period was {e1} commercialized in?",
        "relative": "the time period {e1} was commercialized in",
    },
    "was_revived_in": {
        "statement": "{e1} was revived in the time period {e2}.",
        "question": "What time period was {e1} revived in?",
        "relative": "the time period {e1} was revived in",
    },
    "is_nostalgic_for": {
        "statement": "{e1} is nostalgic for the time period {e2}.",
        "question": "What time period is {e1} nostalgic for?",
        "relative": "the time period {e1} is nostalgic for",
    },
    # ---------- Skill ↔ PhysicalObject ----------
    "requires_skl_obj": {
        "statement": "{e1} requires the object {e2}.",
        "question": "What object does {e1} require?",
        "relative": "the object {e1} requires",
    },
    "maintains_skl_obj": {
        "statement": "{e1} maintains the object {e2}.",
        "question": "What object does {e1} maintain?",
        "relative": "the object {e1} maintains",
    },
    "produces_skl_obj": {
        "statement": "{e1} produces the object {e2}.",
        "question": "What object does {e1} produce?",
        "relative": "the object {e1} produces",
    },
    "repairs_skl_obj": {
        "statement": "{e1} repairs the object {e2}.",
        "question": "What object does {e1} repair?",
        "relative": "the object {e1} repairs",
    },
    "calibrates_skl_obj": {
        "statement": "{e1} calibrates the object {e2}.",
        "question": "What object does {e1} calibrate?",
        "relative": "the object {e1} calibrates",
    },
    "is_enhanced_by_skl_obj": {
        "statement": "{e1} is enhanced by the object {e2}.",
        "question": "What object is {e1} enhanced by?",
        "relative": "the object {e1} is enhanced by",
    },
    "is_limited_by_skl_obj": {
        "statement": "{e1} is limited by the object {e2}.",
        "question": "What object is {e1} limited by?",
        "relative": "the object {e1} is limited by",
    },

    "is_applied_to": {
        "statement": "{e1} is applied to the object {e2}.",
        "question": "What object is {e1} applied to?",
        "relative": "the object {e1} is applied to",
    },
    "is_demonstrated_with": {
        "statement": "{e1} is demonstrated with the object {e2}.",
        "question": "What object is {e1} demonstrated with?",
        "relative": "the object {e1} is demonstrated with",
    },
    "transforms": {
        "statement": "{e1} transforms the object {e2}.",
        "question": "What object does {e1} transform?",
        "relative": "the object {e1} transforms",
    },
    # ---------- Skill ↔ Product ----------
    "improves_skl_prd": {
        "statement": "{e1} improves the product {e2}.",
        "question": "What product does {e1} improve?",
        "relative": "the product {e1} improves",
    },
    "is_enhanced_by_skl_prd": {
        "statement": "{e1} is enhanced by the product {e2}.",
        "question": "What product is {e1} enhanced by?",
        "relative": "the product {e1} is enhanced by",
    },
    "certifies_skl_prd": {
        "statement": "{e1} certifies the product {e2}.",
        "question": "What product does {e1} certify?",
        "relative": "the product {e1} certifies",
    },
    "repairs_skl_prd": {
        "statement": "{e1} repairs the product {e2}.",
        "question": "What product does {e1} repair?",
        "relative": "the product {e1} repairs",
    },
    "is_monetized_by_skl_prd": {
        "statement": "{e1} is monetized by the product {e2}.",
        "question": "What product is {e1} monetized by?",
        "relative": "the product {e1} is monetized by",
    },
    "customizes_skl_prd": {
        "statement": "{e1} customizes the product {e2}.",
        "question": "What product does {e1} customize?",
        "relative": "the product {e1} customizes",
    },

    "enables_creation_of": {
        "statement": "{e1} enables creation of the product {e2}.",
        "question": "What product does {e1} enable creation of?",
        "relative": "the product {e1} enables creation of",
    },
    "is_demonstrated_by": {
        "statement": "{e1} is demonstrated by the product {e2}.",
        "question": "What product is {e1} demonstrated by?",
        "relative": "the product {e1} is demonstrated by",
    },
    "is_required_for": {
        "statement": "{e1} is required for the product {e2}.",
        "question": "What product is {e1} required for?",
        "relative": "the product {e1} is required for",
    },
    "is_automated_by": {
        "statement": "{e1} is automated by the product {e2}.",
        "question": "What product is {e1} automated by?",
        "relative": "the product {e1} is automated by",
    },
    # ---------- Skill ↔ Service ----------
    "enables": {
        "statement": "{e1} enables the service {e2}.",
        "question": "What service does {e1} enable?",
        "relative": "the service {e1} enables",
    },
    "is_taught_by_skl_svc": {
        "statement": "{e1} is taught by the service {e2}.",
        "question": "What service is {e1} taught by?",
        "relative": "the service {e1} is taught by",
    },
    "is_automated_by_skl_svc": {
        "statement": "{e1} is automated by the service {e2}.",
        "question": "What service is {e1} automated by?",
        "relative": "the service {e1} is automated by",
    },
    "enhances": {
        "statement": "{e1} enhances the service {e2}.",
        "question": "What service does {e1} enhance?",
        "relative": "the service {e1} enhances",
    },
    "is_monetized_by_skl_svc": {
        "statement": "{e1} is monetized by the service {e2}.",
        "question": "What service is {e1} monetized by?",
        "relative": "the service {e1} is monetized by",
    },

    "qualifies_for": {
        "statement": "{e1} qualifies for the service {e2}.",
        "question": "What service does {e1} qualify for?",
        "relative": "the service {e1} qualifies for",
    },
    "is_improved_by": {
        "statement": "{e1} is improved by the service {e2}.",
        "question": "What service is {e1} improved by?",
        "relative": "the service {e1} is improved by",
    },
    "is_certified_by": {
        "statement": "{e1} is certified by the service {e2}.",
        "question": "What service is {e1} certified by?",
        "relative": "the service {e1} is certified by",
    },
    "is_required_by": {
        "statement": "{e1} is required by the service {e2}.",
        "question": "What service is {e1} required by?",
        "relative": "the service {e1} is required by",
    },
    "is_benchmarked_by": {
        "statement": "{e1} is benchmarked by the service {e2}.",
        "question": "What service is {e1} benchmarked by?",
        "relative": "the service {e1} is benchmarked by",
    },
    # ---------- Skill ↔ MediaWork ----------
    "is_taught_by_skl_mda": {
        "statement": "{e1} is taught by the media work {e2}.",
        "question": "What media work is {e1} taught by?",
        "relative": "the media work {e1} is taught by",
    },
    "is_documented_in_skl_mda": {
        "statement": "{e1} is documented in the media work {e2}.",
        "question": "What media work documents {e1}?",
        "relative": "the media work that documents {e1}",
    },
    "is_celebrated_in_skl_mda": {
        "statement": "{e1} is celebrated in the media work {e2}.",
        "question": "What media work is {e1} celebrated in?",
        "relative": "the media work {e1} is celebrated in",
    },
    "produces_skl_mda": {
        "statement": "{e1} produces the media work {e2}.",
        "question": "What media work does {e1} produce?",
        "relative": "the media work {e1} produces",
    },
    "is_required_for_skl_mda": {
        "statement": "{e1} is required for the media work {e2}.",
        "question": "What media work is {e1} required for?",
        "relative": "the media work {e1} is required for",
    },
    "is_featured_in_skl_mda": {
        "statement": "{e1} is featured in the media work {e2}.",
        "question": "What media work is {e1} featured in?",
        "relative": "the media work {e1} is featured in",
    },
    "is_trivialized_in_skl_mda": {
        "statement": "{e1} is trivialized in the media work {e2}.",
        "question": "What media work is {e1} trivialized in?",
        "relative": "the media work {e1} is trivialized in",
    },

    "is_expressed_in": {
        "statement": "{e1} is expressed in the media work {e2}.",
        "question": "What media work is {e1} expressed in?",
        "relative": "the media work {e1} is expressed in",
    },
    "is_demonstrated_in": {
        "statement": "{e1} is demonstrated in the media work {e2}.",
        "question": "What media work is {e1} demonstrated in?",
        "relative": "the media work {e1} is demonstrated in",
    },
    "is_preserved_in": {
        "statement": "{e1} is preserved in the media work {e2}.",
        "question": "What media work is {e1} preserved in?",
        "relative": "the media work {e1} is preserved in",
    },
    # ---------- Skill ↔ DigitalTool ----------
    "is_augmented_by_skl_dgt": {
        "statement": "{e1} is augmented by the digital tool {e2}.",
        "question": "What digital tool is {e1} augmented by?",
        "relative": "the digital tool {e1} is augmented by",
    },
    "is_required_for_skl_dgt": {
        "statement": "{e1} is required for the digital tool {e2}.",
        "question": "What digital tool is {e1} required for?",
        "relative": "the digital tool {e1} is required for",
    },
    "is_taught_by_skl_dgt": {
        "statement": "{e1} is taught by the digital tool {e2}.",
        "question": "What digital tool is {e1} taught by?",
        "relative": "the digital tool {e1} is taught by",
    },
    "is_automated_by_skl_dgt": {
        "statement": "{e1} is automated by the digital tool {e2}.",
        "question": "What digital tool is {e1} automated by?",
        "relative": "the digital tool {e1} is automated by",
    },
    "is_measured_by_skl_dgt": {
        "statement": "{e1} is measured by the digital tool {e2}.",
        "question": "What digital tool is {e1} measured by?",
        "relative": "the digital tool {e1} is measured by",
    },
    "is_certified_by_skl_dgt": {
        "statement": "{e1} is certified by the digital tool {e2}.",
        "question": "What digital tool is {e1} certified by?",
        "relative": "the digital tool {e1} is certified by",
    },
    "is_demonstrated_in_skl_dgt": {
        "statement": "{e1} is demonstrated in the digital tool {e2}.",
        "question": "What digital tool is {e1} demonstrated in?",
        "relative": "the digital tool {e1} is demonstrated in",
    },
    "develops_skl_dgt": {
        "statement": "{e1} develops the digital tool {e2}.",
        "question": "What digital tool does {e1} develop?",
        "relative": "the digital tool {e1} develops",
    },
    "is_gamified_by_skl_dgt": {
        "statement": "{e1} is gamified by the digital tool {e2}.",
        "question": "What digital tool is {e1} gamified by?",
        "relative": "the digital tool {e1} is gamified by",
    },

    "is_tracked_by": {
        "statement": "{e1} is tracked by the digital tool {e2}.",
        "question": "What digital tool is {e1} tracked by?",
        "relative": "the digital tool {e1} is tracked by",
    },
    # ---------- Skill ↔ Task ----------
    "enables_skl_tsk": {
        "statement": "{e1} enables the task {e2}.",
        "question": "What task does {e1} enable?",
        "relative": "the task {e1} enables",
    },
    "is_measured_by_skl_tsk": {
        "statement": "{e1} is measured by the task {e2}.",
        "question": "What task is {e1} measured by?",
        "relative": "the task {e1} is measured by",
    },
    "is_required_for_skl_tsk": {
        "statement": "{e1} is required for the task {e2}.",
        "question": "What task is {e1} required for?",
        "relative": "the task {e1} is required for",
    },
    "simplifies_skl_tsk": {
        "statement": "{e1} simplifies the task {e2}.",
        "question": "What task does {e1} simplify?",
        "relative": "the task {e1} simplifies",
    },
    "is_developed_by_skl_tsk": {
        "statement": "{e1} is developed by the task {e2}.",
        "question": "What task develops {e1}?",
        "relative": "the task that develops {e1}",
    },
    "automates_skl_tsk": {
        "statement": "{e1} automates the task {e2}.",
        "question": "What task does {e1} automate?",
        "relative": "the task {e1} automates",
    },
    "is_demonstrated_in_skl_tsk": {
        "statement": "{e1} is demonstrated in the task {e2}.",
        "question": "What task is {e1} demonstrated in?",
        "relative": "the task {e1} is demonstrated in",
    },
    "is_benchmarked_by_skl_tsk": {
        "statement": "{e1} is benchmarked by the task {e2}.",
        "question": "What task is {e1} benchmarked by?",
        "relative": "the task {e1} is benchmarked by",
    },

    "optimizes": {
        "statement": "{e1} optimizes the task {e2}.",
        "question": "What task does {e1} optimize?",
        "relative": "the task {e1} optimizes",
    },
    "is_challenged_by": {
        "statement": "{e1} is challenged by the task {e2}.",
        "question": "What task is {e1} challenged by?",
        "relative": "the task {e1} is challenged by",
    },
    # ---------- Skill ↔ TimePeriod ----------
    "became_obsolete_by_skl_tmp": {
        "statement": "{e1} became obsolete by the time period {e2}.",
        "question": "What time period did {e1} become obsolete by?",
        "relative": "the time period {e1} became obsolete by",
    },
    "emerged_in_skl_tmp": {
        "statement": "{e1} emerged in the time period {e2}.",
        "question": "What time period did {e1} emerge in?",
        "relative": "the time period {e1} emerged in",
    },
    "was_automated_in_skl_tmp": {
        "statement": "{e1} was automated in the time period {e2}.",
        "question": "What time period was {e1} automated in?",
        "relative": "the time period {e1} was automated in",
    },
    "peaked_during_skl_tmp": {
        "statement": "{e1} peaked during the time period {e2}.",
        "question": "What time period did {e1} peak during?",
        "relative": "the time period {e1} peaked during",
    },
    "declined_during_skl_tmp": {
        "statement": "{e1} declined during the time period {e2}.",
        "question": "What time period did {e1} decline during?",
        "relative": "the time period {e1} declined during",
    },
    "was_professionalized_in_skl_tmp": {
        "statement": "{e1} was professionalized in the time period {e2}.",
        "question": "What time period was {e1} professionalized in?",
        "relative": "the time period {e1} was professionalized in",
    },

    "is_mastered_during": {
        "statement": "{e1} is mastered during the time period {e2}.",
        "question": "What time period is {e1} mastered during?",
        "relative": "the time period {e1} is mastered during",
    },
    "was_valued_in": {
        "statement": "{e1} was valued in the time period {e2}.",
        "question": "What time period was {e1} valued in?",
        "relative": "the time period {e1} was valued in",
    },
    "was_standardized_in": {
        "statement": "{e1} was standardized in the time period {e2}.",
        "question": "What time period was {e1} standardized in?",
        "relative": "the time period {e1} was standardized in",
    },
    "was_democratized_in": {
        "statement": "{e1} was democratized in the time period {e2}.",
        "question": "What time period was {e1} democratized in?",
        "relative": "the time period {e1} was democratized in",
    },
    # ---------- PhysicalObject ↔ Product ----------
    "is_replaced_by_obj_prd": {
        "statement": "{e1} is replaced by the product {e2}.",
        "question": "What product is {e1} replaced by?",
        "relative": "the product {e1} is replaced by",
    },
    "is_compatible_with": {
        "statement": "{e1} is compatible with the product {e2}.",
        "question": "What product is {e1} compatible with?",
        "relative": "the product {e1} is compatible with",
    },
    "is_accessory_for": {
        "statement": "{e1} is an accessory for the product {e2}.",
        "question": "What product is {e1} an accessory for?",
        "relative": "the product {e1} is an accessory for",
    },
    "is_damaged_by_obj_prd": {
        "statement": "{e1} is damaged by the product {e2}.",
        "question": "What product damages {e1}?",
        "relative": "the product that damages {e1}",
    },

    "is_component_of": {
        "statement": "{e1} is component of the product {e2}.",
        "question": "What product is {e1} component of?",
        "relative": "the product {e1} is component of",
    },
    "is_packaged_with": {
        "statement": "{e1} is packaged with the product {e2}.",
        "question": "What product is {e1} packaged with?",
        "relative": "the product {e1} is packaged with",
    },
    "is_repurposed_as": {
        "statement": "{e1} is repurposed as the product {e2}.",
        "question": "What product is {e1} repurposed as?",
        "relative": "the product {e1} is repurposed as",
    },
    "is_recycled_into": {
        "statement": "{e1} is recycled into the product {e2}.",
        "question": "What product is {e1} recycled into?",
        "relative": "the product {e1} is recycled into",
    },
    "is_prototype_for": {
        "statement": "{e1} is prototype for the product {e2}.",
        "question": "What product is {e1} prototype for?",
        "relative": "the product {e1} is prototype for",
    },
    "is_displayed_with": {
        "statement": "{e1} is displayed with the product {e2}.",
        "question": "What product is {e1} displayed with?",
        "relative": "the product {e1} is displayed with",
    },
    # ---------- PhysicalObject ↔ Service ----------
    "is_tracked_by_obj_svc": {
        "statement": "{e1} is tracked by the service {e2}.",
        "question": "What service is {e1} tracked by?",
        "relative": "the service {e1} is tracked by",
    },

    "is_maintained_by": {
        "statement": "{e1} is maintained by the service {e2}.",
        "question": "What service is {e1} maintained by?",
        "relative": "the service {e1} is maintained by",
    },
    "is_delivered_via": {
        "statement": "{e1} is delivered via the service {e2}.",
        "question": "What service is {e1} delivered via?",
        "relative": "the service {e1} is delivered via",
    },
    "is_repaired_by": {
        "statement": "{e1} is repaired by the service {e2}.",
        "question": "What service is {e1} repaired by?",
        "relative": "the service {e1} is repaired by",
    },
    "is_insured_by": {
        "statement": "{e1} is insured by the service {e2}.",
        "question": "What service is {e1} insured by?",
        "relative": "the service {e1} is insured by",
    },
    "is_appraised_by": {
        "statement": "{e1} is appraised by the service {e2}.",
        "question": "What service is {e1} appraised by?",
        "relative": "the service {e1} is appraised by",
    },
    "is_disposed_of_by": {
        "statement": "{e1} is disposed of by the service {e2}.",
        "question": "What service is {e1} disposed of by?",
        "relative": "the service {e1} is disposed of by",
    },
    "is_stored_by": {
        "statement": "{e1} is stored by the service {e2}.",
        "question": "What service is {e1} stored by?",
        "relative": "the service {e1} is stored by",
    },
    "is_cleaned_by": {
        "statement": "{e1} is cleaned by the service {e2}.",
        "question": "What service is {e1} cleaned by?",
        "relative": "the service {e1} is cleaned by",
    },
    "is_installed_by": {
        "statement": "{e1} is installed by the service {e2}.",
        "question": "What service is {e1} installed by?",
        "relative": "the service {e1} is installed by",
    },
    # ---------- PhysicalObject ↔ MediaWork ----------
    "is_featured_in_obj_mda": {
        "statement": "{e1} is featured in the media work {e2}.",
        "question": "What media work is {e1} featured in?",
        "relative": "the media work {e1} is featured in",
    },
    "is_subject_of_obj_mda": {
        "statement": "{e1} is the subject of the media work {e2}.",
        "question": "What media work is {e1} the subject of?",
        "relative": "the media work {e1} is the subject of",
    },
    "is_celebrated_in_obj_mda": {
        "statement": "{e1} is celebrated in the media work {e2}.",
        "question": "What media work is {e1} celebrated in?",
        "relative": "the media work {e1} is celebrated in",
    },

    "is_documented_by": {
        "statement": "{e1} is documented by the media work {e2}.",
        "question": "What media work is {e1} documented by?",
        "relative": "the media work {e1} is documented by",
    },
    "is_prop_in": {
        "statement": "{e1} is prop in the media work {e2}.",
        "question": "What media work is {e1} prop in?",
        "relative": "the media work {e1} is prop in",
    },
    "is_advertised_in": {
        "statement": "{e1} is advertised in the media work {e2}.",
        "question": "What media work is {e1} advertised in?",
        "relative": "the media work {e1} is advertised in",
    },
    "is_symbol_in": {
        "statement": "{e1} is symbol in the media work {e2}.",
        "question": "What media work is {e1} symbol in?",
        "relative": "the media work {e1} is symbol in",
    },
    "is_reviewed_in": {
        "statement": "{e1} is reviewed in the media work {e2}.",
        "question": "What media work is {e1} reviewed in?",
        "relative": "the media work {e1} is reviewed in",
    },
    "is_collected_due_to": {
        "statement": "{e1} is collected due to the media work {e2}.",
        "question": "What media work is {e1} collected due to?",
        "relative": "the media work {e1} is collected due to",
    },
    "is_iconic_from": {
        "statement": "{e1} is iconic from the media work {e2}.",
        "question": "What media work is {e1} iconic from?",
        "relative": "the media work {e1} is iconic from",
    },
    # ---------- PhysicalObject ↔ DigitalTool ----------
    "is_tracked_by_obj_dgt": {
        "statement": "{e1} is tracked by the digital tool {e2}.",
        "question": "What digital tool is {e1} tracked by?",
        "relative": "the digital tool {e1} is tracked by",
    },

    "is_controlled_by": {
        "statement": "{e1} is controlled by the digital tool {e2}.",
        "question": "What digital tool is {e1} controlled by?",
        "relative": "the digital tool {e1} is controlled by",
    },
    "is_monitored_by": {
        "statement": "{e1} is monitored by the digital tool {e2}.",
        "question": "What digital tool is {e1} monitored by?",
        "relative": "the digital tool {e1} is monitored by",
    },
    "is_designed_with": {
        "statement": "{e1} is designed with the digital tool {e2}.",
        "question": "What digital tool is {e1} designed with?",
        "relative": "the digital tool {e1} is designed with",
    },
    "is_inventoried_by": {
        "statement": "{e1} is inventoried by the digital tool {e2}.",
        "question": "What digital tool is {e1} inventoried by?",
        "relative": "the digital tool {e1} is inventoried by",
    },
    "is_simulated_in": {
        "statement": "{e1} is simulated in the digital tool {e2}.",
        "question": "What digital tool is {e1} simulated in?",
        "relative": "the digital tool {e1} is simulated in",
    },
    "is_catalogued_by": {
        "statement": "{e1} is catalogued by the digital tool {e2}.",
        "question": "What digital tool is {e1} catalogued by?",
        "relative": "the digital tool {e1} is catalogued by",
    },
    "is_3d_modeled_in": {
        "statement": "{e1} is 3d modeled in the digital tool {e2}.",
        "question": "What digital tool is {e1} 3d modeled in?",
        "relative": "the digital tool {e1} is 3d modeled in",
    },
    "is_authenticated_by": {
        "statement": "{e1} is authenticated by the digital tool {e2}.",
        "question": "What digital tool is {e1} authenticated by?",
        "relative": "the digital tool {e1} is authenticated by",
    },
    "interfaces_with": {
        "statement": "{e1} interfaces with the digital tool {e2}.",
        "question": "What digital tool does {e1} interface with?",
        "relative": "the digital tool {e1} interfaces with",
    },
    # ---------- PhysicalObject ↔ Task ----------
    "is_required_for_obj_tsk": {
        "statement": "{e1} is required for the task {e2}.",
        "question": "What task is {e1} required for?",
        "relative": "the task {e1} is required for",
    },
    "simplifies_obj_tsk": {
        "statement": "{e1} simplifies the task {e2}.",
        "question": "What task does {e1} simplify?",
        "relative": "the task {e1} simplifies",
    },
    "complicates_obj_tsk": {
        "statement": "{e1} complicates the task {e2}.",
        "question": "What task does {e1} complicate?",
        "relative": "the task {e1} complicates",
    },

    "is_produced_by": {
        "statement": "{e1} is produced by the task {e2}.",
        "question": "What task is {e1} produced by?",
        "relative": "the task {e1} is produced by",
    },
    "is_used_in": {
        "statement": "{e1} is used in the task {e2}.",
        "question": "What task is {e1} used in?",
        "relative": "the task {e1} is used in",
    },
    "is_transported_during": {
        "statement": "{e1} is transported during the task {e2}.",
        "question": "What task is {e1} transported during?",
        "relative": "the task {e1} is transported during",
    },
    "is_calibrated_during": {
        "statement": "{e1} is calibrated during the task {e2}.",
        "question": "What task is {e1} calibrated during?",
        "relative": "the task {e1} is calibrated during",
    },
    "is_damaged_during": {
        "statement": "{e1} is damaged during the task {e2}.",
        "question": "What task is {e1} damaged during?",
        "relative": "the task {e1} is damaged during",
    },
    "is_assembled_during": {
        "statement": "{e1} is assembled during the task {e2}.",
        "question": "What task is {e1} assembled during?",
        "relative": "the task {e1} is assembled during",
    },
    "is_disposed_of_after": {
        "statement": "{e1} is disposed of after the task {e2}.",
        "question": "What task is {e1} disposed of after?",
        "relative": "the task {e1} is disposed of after",
    },
    # ---------- PhysicalObject ↔ TimePeriod ----------
    "was_standardized_in_obj_tmp": {
        "statement": "{e1} was standardized in the time period {e2}.",
        "question": "What time period was {e1} standardized in?",
        "relative": "the time period {e1} was standardized in",
    },

    "was_manufactured_in": {
        "statement": "{e1} was manufactured in the time period {e2}.",
        "question": "What time period was {e1} manufactured in?",
        "relative": "the time period {e1} was manufactured in",
    },
    "is_antique_from": {
        "statement": "{e1} is antique from the time period {e2}.",
        "question": "What time period is {e1} antique from?",
        "relative": "the time period {e1} is antique from",
    },
    "was_invented_in": {
        "statement": "{e1} was invented in the time period {e2}.",
        "question": "What time period was {e1} invented in?",
        "relative": "the time period {e1} was invented in",
    },
    "was_discontinued_in": {
        "statement": "{e1} was discontinued in the time period {e2}.",
        "question": "What time period was {e1} discontinued in?",
        "relative": "the time period {e1} was discontinued in",
    },
    "was_popular_during": {
        "statement": "{e1} was popular during the time period {e2}.",
        "question": "What time period was {e1} popular during?",
        "relative": "the time period {e1} was popular during",
    },
    "was_obsolete_by": {
        "statement": "{e1} was obsolete by the time period {e2}.",
        "question": "What time period was {e1} obsolete by?",
        "relative": "the time period {e1} was obsolete by",
    },
    "was_patented_in": {
        "statement": "{e1} was patented in the time period {e2}.",
        "question": "What time period was {e1} patented in?",
        "relative": "the time period {e1} was patented in",
    },
    "was_mass_produced_in": {
        "statement": "{e1} was mass produced in the time period {e2}.",
        "question": "What time period was {e1} mass produced in?",
        "relative": "the time period {e1} was mass produced in",
    },
    "was_collectible_in": {
        "statement": "{e1} was collectible in the time period {e2}.",
        "question": "What time period was {e1} collectible in?",
        "relative": "the time period {e1} was collectible in",
    },
    # ---------- Product ↔ Service ----------
    "is_bundled_with": {
        "statement": "{e1} is bundled with the service {e2}.",
        "question": "What service is {e1} bundled with?",
        "relative": "the service {e1} is bundled with",
    },
    "is_installed_by_prd_svc": {
        "statement": "{e1} is installed by the service {e2}.",
        "question": "What service is {e1} installed by?",
        "relative": "the service {e1} is installed by",
    },
    "is_repaired_by_prd_svc": {
        "statement": "{e1} is repaired by the service {e2}.",
        "question": "What service is {e1} repaired by?",
        "relative": "the service {e1} is repaired by",
    },
    "is_supported_by_prd_svc": {
        "statement": "{e1} is supported by the service {e2}.",
        "question": "What service is {e1} supported by?",
        "relative": "the service {e1} is supported by",
    },
    "is_insured_by_prd_svc": {
        "statement": "{e1} is insured by the service {e2}.",
        "question": "What service is {e1} insured by?",
        "relative": "the service {e1} is insured by",
    },

    "has_warranty_from": {
        "statement": "{e1} has warranty from the service {e2}.",
        "question": "What service does {e1} have warranty from?",
        "relative": "the service {e1} has warranty from",
    },
    "is_delivered_by": {
        "statement": "{e1} is delivered by the service {e2}.",
        "question": "What service is {e1} delivered by?",
        "relative": "the service {e1} is delivered by",
    },
    "is_financed_by": {
        "statement": "{e1} is financed by the service {e2}.",
        "question": "What service is {e1} financed by?",
        "relative": "the service {e1} is financed by",
    },
    "is_recycled_by": {
        "statement": "{e1} is recycled by the service {e2}.",
        "question": "What service is {e1} recycled by?",
        "relative": "the service {e1} is recycled by",
    },
    "is_subscribed_with": {
        "statement": "{e1} is subscribed with the service {e2}.",
        "question": "What service is {e1} subscribed with?",
        "relative": "the service {e1} is subscribed with",
    },
    # ---------- Product ↔ MediaWork ----------
    "is_advertised_in_prd_mda": {
        "statement": "{e1} is advertised in the media work {e2}.",
        "question": "What media work is {e1} advertised in?",
        "relative": "the media work {e1} is advertised in",
    },
    "is_featured_in_prd_mda": {
        "statement": "{e1} is featured in the media work {e2}.",
        "question": "What media work is {e1} featured in?",
        "relative": "the media work {e1} is featured in",
    },
    "inspires_prd_mda": {
        "statement": "{e1} inspires the media work {e2}.",
        "question": "What media work does {e1} inspire?",
        "relative": "the media work {e1} inspires",
    },
    "is_satirized_in_prd_mda": {
        "statement": "{e1} is satirized in the media work {e2}.",
        "question": "What media work is {e1} satirized in?",
        "relative": "the media work {e1} is satirized in",
    },

    "is_reviewed_by": {
        "statement": "{e1} is reviewed by the media work {e2}.",
        "question": "What media work is {e1} reviewed by?",
        "relative": "the media work {e1} is reviewed by",
    },
    "is_placed_in": {
        "statement": "{e1} is placed in the media work {e2}.",
        "question": "What media work is {e1} placed in?",
        "relative": "the media work {e1} is placed in",
    },
    "is_criticized_in": {
        "statement": "{e1} is criticized in the media work {e2}.",
        "question": "What media work is {e1} criticized in?",
        "relative": "the media work {e1} is criticized in",
    },
    "is_compared_in": {
        "statement": "{e1} is compared in the media work {e2}.",
        "question": "What media work is {e1} compared in?",
        "relative": "the media work {e1} is compared in",
    },
    "is_unboxed_in": {
        "statement": "{e1} is unboxed in the media work {e2}.",
        "question": "What media work is {e1} unboxed in?",
        "relative": "the media work {e1} is unboxed in",
    },
    "is_tutorial_subject_in": {
        "statement": "{e1} is tutorial subject in the media work {e2}.",
        "question": "What media work is {e1} tutorial subject in?",
        "relative": "the media work {e1} is tutorial subject in",
    },
    # ---------- Product ↔ DigitalTool ----------
    "is_compatible_with_prd_dgt": {
        "statement": "{e1} is compatible with the digital tool {e2}.",
        "question": "What digital tool is {e1} compatible with?",
        "relative": "the digital tool {e1} is compatible with",
    },
    "is_designed_with_prd_dgt": {
        "statement": "{e1} is designed with the digital tool {e2}.",
        "question": "What digital tool is {e1} designed with?",
        "relative": "the digital tool {e1} is designed with",
    },
    "is_tracked_by_prd_dgt": {
        "statement": "{e1} is tracked by the digital tool {e2}.",
        "question": "What digital tool is {e1} tracked by?",
        "relative": "the digital tool {e1} is tracked by",
    },
    "integrates_with": {
        "statement": "{e1} integrates with the digital tool {e2}.",
        "question": "What digital tool does {e1} integrate with?",
        "relative": "the digital tool {e1} integrates with",
    },
    "is_controlled_by_prd_dgt": {
        "statement": "{e1} is controlled by the digital tool {e2}.",
        "question": "What digital tool is {e1} controlled by?",
        "relative": "the digital tool {e1} is controlled by",
    },
    "is_simulated_in_prd_dgt": {
        "statement": "{e1} is simulated in the digital tool {e2}.",
        "question": "What digital tool is {e1} simulated in?",
        "relative": "the digital tool {e1} is simulated in",
    },

    "is_managed_by": {
        "statement": "{e1} is managed by the digital tool {e2}.",
        "question": "What digital tool is {e1} managed by?",
        "relative": "the digital tool {e1} is managed by",
    },
    "is_configured_by": {
        "statement": "{e1} is configured by the digital tool {e2}.",
        "question": "What digital tool is {e1} configured by?",
        "relative": "the digital tool {e1} is configured by",
    },
    "is_sold_via": {
        "statement": "{e1} is sold via the digital tool {e2}.",
        "question": "What digital tool is {e1} sold via?",
        "relative": "the digital tool {e1} is sold via",
    },
    "is_reviewed_on": {
        "statement": "{e1} is reviewed on the digital tool {e2}.",
        "question": "What digital tool is {e1} reviewed on?",
        "relative": "the digital tool {e1} is reviewed on",
    },
    # ---------- Product ↔ Task ----------
    "is_assembled_during_prd_tsk": {
        "statement": "{e1} is assembled during the task {e2}.",
        "question": "What task is {e1} assembled during?",
        "relative": "the task {e1} is assembled during",
    },
    "simplifies_prd_tsk": {
        "statement": "{e1} simplifies the task {e2}.",
        "question": "What task does {e1} simplify?",
        "relative": "the task {e1} simplifies",
    },
    "is_required_for_prd_tsk": {
        "statement": "{e1} is required for the task {e2}.",
        "question": "What task is {e1} required for?",
        "relative": "the task {e1} is required for",
    },
    "complicates_prd_tsk": {
        "statement": "{e1} complicates the task {e2}.",
        "question": "What task does {e1} complicate?",
        "relative": "the task {e1} complicates",
    },
    "automates_prd_tsk": {
        "statement": "{e1} automates the task {e2}.",
        "question": "What task does {e1} automate?",
        "relative": "the task {e1} automates",
    },

    "is_designed_for": {
        "statement": "{e1} is designed for the task {e2}.",
        "question": "What task is {e1} designed for?",
        "relative": "the task {e1} is designed for",
    },
    "is_tested_during": {
        "statement": "{e1} is tested during the task {e2}.",
        "question": "What task is {e1} tested during?",
        "relative": "the task {e1} is tested during",
    },
    "is_packaged_during": {
        "statement": "{e1} is packaged during the task {e2}.",
        "question": "What task is {e1} packaged during?",
        "relative": "the task {e1} is packaged during",
    },
    "is_quality_checked_during": {
        "statement": "{e1} is quality checked during the task {e2}.",
        "question": "What task is {e1} quality checked during?",
        "relative": "the task {e1} is quality checked during",
    },
    "is_shipped_during": {
        "statement": "{e1} is shipped during the task {e2}.",
        "question": "What task is {e1} shipped during?",
        "relative": "the task {e1} is shipped during",
    },
    # ---------- Product ↔ TimePeriod ----------
    "was_discontinued_in_prd_tmp": {
        "statement": "{e1} was discontinued in the time period {e2}.",
        "question": "What time period was {e1} discontinued in?",
        "relative": "the time period {e1} was discontinued in",
    },
    "was_popular_during_prd_tmp": {
        "statement": "{e1} was popular during the time period {e2}.",
        "question": "What time period was {e1} popular during?",
        "relative": "the time period {e1} was popular during",
    },
    "was_patented_in_prd_tmp": {
        "statement": "{e1} was patented in the time period {e2}.",
        "question": "What time period was {e1} patented in?",
        "relative": "the time period {e1} was patented in",
    },
    "was_obsolete_by_prd_tmp": {
        "statement": "{e1} was obsolete by the time period {e2}.",
        "question": "What time period was {e1} obsolete by?",
        "relative": "the time period {e1} was obsolete by",
    },

    "was_launched_in": {
        "statement": "{e1} was launched in the time period {e2}.",
        "question": "What time period was {e1} launched in?",
        "relative": "the time period {e1} was launched in",
    },
    "was_recalled_in": {
        "statement": "{e1} was recalled in the time period {e2}.",
        "question": "What time period was {e1} recalled in?",
        "relative": "the time period {e1} was recalled in",
    },
    "was_updated_in": {
        "statement": "{e1} was updated in the time period {e2}.",
        "question": "What time period was {e1} updated in?",
        "relative": "the time period {e1} was updated in",
    },
    "dominated_during": {
        "statement": "{e1} dominated during the time period {e2}.",
        "question": "What time period did {e1} dominate during?",
        "relative": "the time period {e1} dominated during",
    },
    "was_revolutionary_in": {
        "statement": "{e1} was revolutionary in the time period {e2}.",
        "question": "What time period was {e1} revolutionary in?",
        "relative": "the time period {e1} was revolutionary in",
    },
    "was_rebranded_in": {
        "statement": "{e1} was rebranded in the time period {e2}.",
        "question": "What time period was {e1} rebranded in?",
        "relative": "the time period {e1} was rebranded in",
    },
    # ---------- Service ↔ MediaWork ----------
    "is_advertised_in_svc_mda": {
        "statement": "{e1} is advertised in the media work {e2}.",
        "question": "What media work is {e1} advertised in?",
        "relative": "the media work {e1} is advertised in",
    },
    "is_reviewed_by_svc_mda": {
        "statement": "{e1} is reviewed by the media work {e2}.",
        "question": "What media work is {e1} reviewed by?",
        "relative": "the media work {e1} is reviewed by",
    },
    "is_featured_in_svc_mda": {
        "statement": "{e1} is featured in the media work {e2}.",
        "question": "What media work is {e1} featured in?",
        "relative": "the media work {e1} is featured in",
    },
    "is_criticized_in_svc_mda": {
        "statement": "{e1} is criticized in the media work {e2}.",
        "question": "What media work is {e1} criticized in?",
        "relative": "the media work {e1} is criticized in",
    },
    "is_documented_in_svc_mda": {
        "statement": "{e1} is documented in the media work {e2}.",
        "question": "What media work documents {e1}?",
        "relative": "the media work that documents {e1}",
    },
    "sponsors_svc_mda": {
        "statement": "{e1} sponsors the media work {e2}.",
        "question": "What media work does {e1} sponsor?",
        "relative": "the media work {e1} sponsors",
    },
    "distributes_svc_mda": {
        "statement": "{e1} distributes the media work {e2}.",
        "question": "What media work does {e1} distribute?",
        "relative": "the media work {e1} distributes",
    },
    "is_tutorial_subject_in_svc_mda": {
        "statement": "{e1} is tutorial subject in the media work {e2}.",
        "question": "What media work is {e1} tutorial subject in?",
        "relative": "the media work {e1} is tutorial subject in",
    },
    "is_compared_in_svc_mda": {
        "statement": "{e1} is compared in the media work {e2}.",
        "question": "What media work is {e1} compared in?",
        "relative": "the media work {e1} is compared in",
    },
    "is_satirized_in_svc_mda": {
        "statement": "{e1} is satirized in the media work {e2}.",
        "question": "What media work is {e1} satirized in?",
        "relative": "the media work {e1} is satirized in",
    },

    # ---------- Service ↔ DigitalTool ----------
    "is_delivered_via_svc_dgt": {
        "statement": "{e1} is delivered via the digital tool {e2}.",
        "question": "What digital tool is {e1} delivered via?",
        "relative": "the digital tool {e1} is delivered via",
    },
    "is_monitored_by_svc_dgt": {
        "statement": "{e1} is monitored by the digital tool {e2}.",
        "question": "What digital tool is {e1} monitored by?",
        "relative": "the digital tool {e1} is monitored by",
    },
    "integrates_with_svc_dgt": {
        "statement": "{e1} integrates with the digital tool {e2}.",
        "question": "What digital tool does {e1} integrate with?",
        "relative": "the digital tool {e1} integrates with",
    },
    "is_managed_by_svc_dgt": {
        "statement": "{e1} is managed by the digital tool {e2}.",
        "question": "What digital tool is {e1} managed by?",
        "relative": "the digital tool {e1} is managed by",
    },
    "is_automated_by_svc_dgt": {
        "statement": "{e1} is automated by the digital tool {e2}.",
        "question": "What digital tool is {e1} automated by?",
        "relative": "the digital tool {e1} is automated by",
    },
    "is_tracked_by_svc_dgt": {
        "statement": "{e1} is tracked by the digital tool {e2}.",
        "question": "What digital tool is {e1} tracked by?",
        "relative": "the digital tool {e1} is tracked by",
    },
    "is_reviewed_on_svc_dgt": {
        "statement": "{e1} is reviewed on the digital tool {e2}.",
        "question": "What digital tool is {e1} reviewed on?",
        "relative": "the digital tool {e1} is reviewed on",
    },
    "is_disrupted_by_svc_dgt": {
        "statement": "{e1} is disrupted by the digital tool {e2}.",
        "question": "What digital tool disrupts {e1}?",
        "relative": "the digital tool that disrupts {e1}",
    },

    "is_booked_via": {
        "statement": "{e1} is booked via the digital tool {e2}.",
        "question": "What digital tool is {e1} booked via?",
        "relative": "the digital tool {e1} is booked via",
    },
    "is_paid_via": {
        "statement": "{e1} is paid via the digital tool {e2}.",
        "question": "What digital tool is {e1} paid via?",
        "relative": "the digital tool {e1} is paid via",
    },
    # ---------- Service ↔ Task ----------
    "requires_svc_tsk": {
        "statement": "{e1} requires the task {e2}.",
        "question": "What task does {e1} require?",
        "relative": "the task {e1} requires",
    },
    "automates_svc_tsk": {
        "statement": "{e1} automates the task {e2}.",
        "question": "What task does {e1} automate?",
        "relative": "the task {e1} automates",
    },
    "simplifies_svc_tsk": {
        "statement": "{e1} simplifies the task {e2}.",
        "question": "What task does {e1} simplify?",
        "relative": "the task {e1} simplifies",
    },
    "schedules_svc_tsk": {
        "statement": "{e1} schedules the task {e2}.",
        "question": "What task does {e1} schedule?",
        "relative": "the task {e1} schedules",
    },
    "assigns_svc_tsk": {
        "statement": "{e1} assigns the task {e2}.",
        "question": "What task does {e1} assign?",
        "relative": "the task {e1} assigns",
    },
    "documents_svc_tsk": {
        "statement": "{e1} documents the task {e2}.",
        "question": "What task does {e1} document?",
        "relative": "the task {e1} documents",
    },
    "is_measured_by_svc_tsk": {
        "statement": "{e1} is measured by the task {e2}.",
        "question": "What task is {e1} measured by?",
        "relative": "the task {e1} is measured by",
    },

    "fulfills": {
        "statement": "{e1} fulfills the task {e2}.",
        "question": "What task does {e1} fulfill?",
        "relative": "the task {e1} fulfills",
    },
    "tracks": {
        "statement": "{e1} tracks the task {e2}.",
        "question": "What task does {e1} track?",
        "relative": "the task {e1} tracks",
    },
    "is_triggered_by": {
        "statement": "{e1} is triggered by the task {e2}.",
        "question": "What task is {e1} triggered by?",
        "relative": "the task {e1} is triggered by",
    },
    # ---------- Service ↔ TimePeriod ----------
    "was_launched_in_svc_tmp": {
        "statement": "{e1} was launched in the time period {e2}.",
        "question": "What time period was {e1} launched in?",
        "relative": "the time period {e1} was launched in",
    },
    "was_discontinued_in_svc_tmp": {
        "statement": "{e1} was discontinued in the time period {e2}.",
        "question": "What time period was {e1} discontinued in?",
        "relative": "the time period {e1} was discontinued in",
    },
    "expanded_during_svc_tmp": {
        "statement": "{e1} expanded during the time period {e2}.",
        "question": "What time period did {e1} expand during?",
        "relative": "the time period {e1} expanded during",
    },
    "was_disrupted_in_svc_tmp": {
        "statement": "{e1} was disrupted in the time period {e2}.",
        "question": "What time period was {e1} disrupted in?",
        "relative": "the time period {e1} was disrupted in",
    },
    "was_regulated_in_svc_tmp": {
        "statement": "{e1} was regulated in the time period {e2}.",
        "question": "What time period was {e1} regulated in?",
        "relative": "the time period {e1} was regulated in",
    },
    "peaked_during_svc_tmp": {
        "statement": "{e1} peaked during the time period {e2}.",
        "question": "What time period did {e1} peak during?",
        "relative": "the time period {e1} peaked during",
    },
    "was_privatized_in_svc_tmp": {
        "statement": "{e1} was privatized in the time period {e2}.",
        "question": "What time period was {e1} privatized in?",
        "relative": "the time period {e1} was privatized in",
    },

    "is_available_during": {
        "statement": "{e1} is available during the time period {e2}.",
        "question": "What time period is {e1} available during?",
        "relative": "the time period {e1} is available during",
    },
    "was_suspended_in": {
        "statement": "{e1} was suspended in the time period {e2}.",
        "question": "What time period was {e1} suspended in?",
        "relative": "the time period {e1} was suspended in",
    },
    "was_deregulated_in": {
        "statement": "{e1} was deregulated in the time period {e2}.",
        "question": "What time period was {e1} deregulated in?",
        "relative": "the time period {e1} was deregulated in",
    },
    # ---------- MediaWork ↔ DigitalTool ----------
    "is_reviewed_on_mda_dgt": {
        "statement": "{e1} is reviewed on the digital tool {e2}.",
        "question": "What digital tool is {e1} reviewed on?",
        "relative": "the digital tool {e1} is reviewed on",
    },

    "was_created_with": {
        "statement": "{e1} was created with the digital tool {e2}.",
        "question": "What digital tool was {e1} created with?",
        "relative": "the digital tool {e1} was created with",
    },
    "is_distributed_via": {
        "statement": "{e1} is distributed via the digital tool {e2}.",
        "question": "What digital tool is {e1} distributed via?",
        "relative": "the digital tool {e1} is distributed via",
    },
    "is_edited_with": {
        "statement": "{e1} is edited with the digital tool {e2}.",
        "question": "What digital tool is {e1} edited with?",
        "relative": "the digital tool {e1} is edited with",
    },
    "is_streamed_on": {
        "statement": "{e1} is streamed on the digital tool {e2}.",
        "question": "What digital tool is {e1} streamed on?",
        "relative": "the digital tool {e1} is streamed on",
    },
    "is_archived_in": {
        "statement": "{e1} is archived in the digital tool {e2}.",
        "question": "What digital tool is {e1} archived in?",
        "relative": "the digital tool {e1} is archived in",
    },
    "is_discovered_via": {
        "statement": "{e1} is discovered via the digital tool {e2}.",
        "question": "What digital tool is {e1} discovered via?",
        "relative": "the digital tool {e1} is discovered via",
    },
    "is_pirated_on": {
        "statement": "{e1} is pirated on the digital tool {e2}.",
        "question": "What digital tool is {e1} pirated on?",
        "relative": "the digital tool {e1} is pirated on",
    },
    "is_monetized_via": {
        "statement": "{e1} is monetized via the digital tool {e2}.",
        "question": "What digital tool is {e1} monetized via?",
        "relative": "the digital tool {e1} is monetized via",
    },
    "is_recommended_by": {
        "statement": "{e1} is recommended by the digital tool {e2}.",
        "question": "What digital tool is {e1} recommended by?",
        "relative": "the digital tool {e1} is recommended by",
    },
    # ---------- MediaWork ↔ Task ----------
    "documents_mda_tsk": {
        "statement": "{e1} documents the task {e2}.",
        "question": "What task does {e1} document?",
        "relative": "the task {e1} documents",
    },
    "inspires_mda_tsk": {
        "statement": "{e1} inspires the task {e2}.",
        "question": "What task does {e1} inspire?",
        "relative": "the task {e1} inspires",
    },
    "teaches_mda_tsk": {
        "statement": "{e1} teaches the task {e2}.",
        "question": "What task does {e1} teach?",
        "relative": "the task {e1} teaches",
    },
    "distracts_from_mda_tsk": {
        "statement": "{e1} distracts from the task {e2}.",
        "question": "What task does {e1} distract from?",
        "relative": "the task {e1} distracts from",
    },
    "is_required_for_mda_tsk": {
        "statement": "{e1} is required for the task {e2}.",
        "question": "What task is {e1} required for?",
        "relative": "the task {e1} is required for",
    },
    "simplifies_mda_tsk": {
        "statement": "{e1} simplifies the task {e2}.",
        "question": "What task does {e1} simplify?",
        "relative": "the task {e1} simplifies",
    },
    "motivates_mda_tsk": {
        "statement": "{e1} motivates the task {e2}.",
        "question": "What task does {e1} motivate?",
        "relative": "the task {e1} motivates",
    },

    "is_created_during": {
        "statement": "{e1} is created during the task {e2}.",
        "question": "What task is {e1} created during?",
        "relative": "the task {e1} is created during",
    },
    "is_referenced_in": {
        "statement": "{e1} is referenced in the task {e2}.",
        "question": "What task is {e1} referenced in?",
        "relative": "the task {e1} is referenced in",
    },
    "is_reviewed_during": {
        "statement": "{e1} is reviewed during the task {e2}.",
        "question": "What task is {e1} reviewed during?",
        "relative": "the task {e1} is reviewed during",
    },
    # ---------- MediaWork ↔ TimePeriod ----------
    "was_banned_in_mda_tmp": {
        "statement": "{e1} was banned in the time period {e2}.",
        "question": "What time period was {e1} banned in?",
        "relative": "the time period {e1} was banned in",
    },
    "was_influential_in_mda_tmp": {
        "statement": "{e1} was influential in the time period {e2}.",
        "question": "What time period was {e1} influential in?",
        "relative": "the time period {e1} was influential in",
    },

    "was_published_in": {
        "statement": "{e1} was published in the time period {e2}.",
        "question": "What time period was {e1} published in?",
        "relative": "the time period {e1} was published in",
    },
    "is_set_in": {
        "statement": "{e1} is set in the time period {e2}.",
        "question": "What time period is {e1} set in?",
        "relative": "the time period {e1} is set in",
    },
    "was_celebrated_in": {
        "statement": "{e1} was celebrated in the time period {e2}.",
        "question": "What time period was {e1} celebrated in?",
        "relative": "the time period {e1} was celebrated in",
    },
    "was_rediscovered_in": {
        "statement": "{e1} was rediscovered in the time period {e2}.",
        "question": "What time period was {e1} rediscovered in?",
        "relative": "the time period {e1} was rediscovered in",
    },
    "was_controversial_in": {
        "statement": "{e1} was controversial in the time period {e2}.",
        "question": "What time period was {e1} controversial in?",
        "relative": "the time period {e1} was controversial in",
    },
    "defined": {
        "statement": "{e1} defined the time period {e2}.",
        "question": "What time period did {e1} define?",
        "relative": "the time period {e1} defined",
    },
    "was_adapted_in": {
        "statement": "{e1} was adapted in the time period {e2}.",
        "question": "What time period was {e1} adapted in?",
        "relative": "the time period {e1} was adapted in",
    },
    "was_censored_in": {
        "statement": "{e1} was censored in the time period {e2}.",
        "question": "What time period was {e1} censored in?",
        "relative": "the time period {e1} was censored in",
    },
    # ---------- DigitalTool ↔ Task ----------
    "automates_dgt_tsk": {
        "statement": "{e1} automates the task {e2}.",
        "question": "What task does {e1} automate?",
        "relative": "the task {e1} automates",
    },
    "facilitates_dgt_tsk": {
        "statement": "{e1} facilitates the task {e2}.",
        "question": "What task does {e1} facilitate?",
        "relative": "the task {e1} facilitates",
    },
    "tracks_dgt_tsk": {
        "statement": "{e1} tracks the task {e2}.",
        "question": "What task does {e1} track?",
        "relative": "the task {e1} tracks",
    },
    "schedules_dgt_tsk": {
        "statement": "{e1} schedules the task {e2}.",
        "question": "What task does {e1} schedule?",
        "relative": "the task {e1} schedules",
    },
    "assigns_dgt_tsk": {
        "statement": "{e1} assigns the task {e2}.",
        "question": "What task does {e1} assign?",
        "relative": "the task {e1} assigns",
    },
    "documents_dgt_tsk": {
        "statement": "{e1} documents the task {e2}.",
        "question": "What task does {e1} document?",
        "relative": "the task {e1} documents",
    },
    "simplifies_dgt_tsk": {
        "statement": "{e1} simplifies the task {e2}.",
        "question": "What task does {e1} simplify?",
        "relative": "the task {e1} simplifies",
    },
    "complicates_dgt_tsk": {
        "statement": "{e1} complicates the task {e2}.",
        "question": "What task does {e1} complicate?",
        "relative": "the task {e1} complicates",
    },
    "is_required_for_dgt_tsk": {
        "statement": "{e1} is required for the task {e2}.",
        "question": "What task is {e1} required for?",
        "relative": "the task {e1} is required for",
    },

    "visualizes": {
        "statement": "{e1} visualizes the task {e2}.",
        "question": "What task does {e1} visualize?",
        "relative": "the task {e1} visualizes",
    },
    # ---------- DigitalTool ↔ TimePeriod ----------
    "was_popular_during_dgt_tmp": {
        "statement": "{e1} was popular during the time period {e2}.",
        "question": "What time period was {e1} popular during?",
        "relative": "the time period {e1} was popular during",
    },
    "was_updated_in_dgt_tmp": {
        "statement": "{e1} was updated in the time period {e2}.",
        "question": "What time period was {e1} updated in?",
        "relative": "the time period {e1} was updated in",
    },
    "was_acquired_in_dgt_tmp": {
        "statement": "{e1} was acquired in the time period {e2}.",
        "question": "What time period was {e1} acquired in?",
        "relative": "the time period {e1} was acquired in",
    },
    "dominated_during_dgt_tmp": {
        "statement": "{e1} dominated during the time period {e2}.",
        "question": "What time period did {e1} dominate during?",
        "relative": "the time period {e1} dominated during",
    },
    "was_disrupted_in_dgt_tmp": {
        "statement": "{e1} was disrupted in the time period {e2}.",
        "question": "What time period was {e1} disrupted in?",
        "relative": "the time period {e1} was disrupted in",
    },

    "was_released_in": {
        "statement": "{e1} was released in the time period {e2}.",
        "question": "What time period was {e1} released in?",
        "relative": "the time period {e1} was released in",
    },
    "was_deprecated_in": {
        "statement": "{e1} was deprecated in the time period {e2}.",
        "question": "What time period was {e1} deprecated in?",
        "relative": "the time period {e1} was deprecated in",
    },
    "was_open_sourced_in": {
        "statement": "{e1} was open sourced in the time period {e2}.",
        "question": "What time period was {e1} open sourced in?",
        "relative": "the time period {e1} was open sourced in",
    },
    "was_forked_in": {
        "statement": "{e1} was forked in the time period {e2}.",
        "question": "What time period was {e1} forked in?",
        "relative": "the time period {e1} was forked in",
    },
    "was_sunset_in": {
        "statement": "{e1} was sunset in the time period {e2}.",
        "question": "What time period was {e1} sunset in?",
        "relative": "the time period {e1} was sunset in",
    },
    # ---------- Task ↔ TimePeriod ----------
    "was_cancelled_in_tsk_tmp": {
        "statement": "{e1} was cancelled in the time period {e2}.",
        "question": "What time period was {e1} cancelled in?",
        "relative": "the time period {e1} was cancelled in",
    },
    "recurs_during_tsk_tmp": {
        "statement": "{e1} recurs during the time period {e2}.",
        "question": "What time period does {e1} recur during?",
        "relative": "the time period {e1} recurs during",
    },
    "was_automated_in_tsk_tmp": {
        "statement": "{e1} was automated in the time period {e2}.",
        "question": "What time period was {e1} automated in?",
        "relative": "the time period {e1} was automated in",
    },
    "peaked_during_tsk_tmp": {
        "statement": "{e1} peaked during the time period {e2}.",
        "question": "What time period did {e1} peak during?",
        "relative": "the time period {e1} peaked during",
    },
    "was_standardized_in_tsk_tmp": {
        "statement": "{e1} was standardized in the time period {e2}.",
        "question": "What time period was {e1} standardized in?",
        "relative": "the time period {e1} was standardized in",
    },

    "is_scheduled_for": {
        "statement": "{e1} is scheduled for the time period {e2}.",
        "question": "What time period is {e1} scheduled for?",
        "relative": "the time period {e1} is scheduled for",
    },
    "was_completed_in": {
        "statement": "{e1} was completed in the time period {e2}.",
        "question": "What time period was {e1} completed in?",
        "relative": "the time period {e1} was completed in",
    },
    "is_due_in": {
        "statement": "{e1} is due in the time period {e2}.",
        "question": "What time period is {e1} due in?",
        "relative": "the time period {e1} is due in",
    },
    "was_delayed_until": {
        "statement": "{e1} was delayed until the time period {e2}.",
        "question": "What time period was {e1} delayed until?",
        "relative": "the time period {e1} was delayed until",
    },
    "was_outsourced_in": {
        "statement": "{e1} was outsourced in the time period {e2}.",
        "question": "What time period was {e1} outsourced in?",
        "relative": "the time period {e1} was outsourced in",
    },
}
