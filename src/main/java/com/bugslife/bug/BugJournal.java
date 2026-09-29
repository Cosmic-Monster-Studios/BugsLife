package com.bugslife.bug;

import com.mojang.serialization.Codec;

import java.util.HashMap;
import java.util.Map;

/** Per-player record of every bug species caught and how many times. Stored as a player attachment. */
public class BugJournal {
    public static final Codec<BugJournal> CODEC = Codec.unboundedMap(Codec.STRING, Codec.INT)
            .xmap(BugJournal::new, j -> j.caught);

    private final Map<String, Integer> caught;

    public BugJournal() {
        this(new HashMap<>());
    }

    public BugJournal(Map<String, Integer> caught) {
        this.caught = new HashMap<>(caught);
    }

    /** @return true if this was the first of its species */
    public boolean record(BugSpecies species) {
        int before = caught.getOrDefault(species.id(), 0);
        caught.put(species.id(), before + 1);
        return before == 0;
    }

    public int count(BugSpecies species) {
        return caught.getOrDefault(species.id(), 0);
    }

    public int discovered() {
        int n = 0;
        for (BugSpecies s : BugSpecies.values()) {
            if (count(s) > 0) n++;
        }
        return n;
    }

    public Map<String, Integer> asMap() {
        return caught;
    }
}
