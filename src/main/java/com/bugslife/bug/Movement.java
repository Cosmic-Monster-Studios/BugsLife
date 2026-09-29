package com.bugslife.bug;

/** How a bug gets around. */
public enum Movement {
    /** Walks on the ground. */
    CRAWL,
    /** Walks and climbs walls and tree trunks like a spider, and can cling to bark. */
    CLIMB,
    /** Flies, landing now and then to rest. */
    FLY,
    /** Walks in short bursts of hops. */
    HOP,
    /** Stands and skates on the surface of water. */
    SKATE,
    /** Hangs motionless from a cave ceiling. */
    HANG,
    /** Swims freely underwater. */
    SWIM,
    /** Crawls along the bottom of rivers and seas, never needing air. */
    AQUATIC
}
