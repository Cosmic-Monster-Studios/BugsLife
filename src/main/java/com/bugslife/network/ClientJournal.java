package com.bugslife.network;

import com.bugslife.bug.BugJournal;

import java.util.Map;

/** The local player's journal as last synced from the server. Holds no client-only classes. */
public final class ClientJournal {
    private static BugJournal journal = new BugJournal();

    private ClientJournal() {
    }

    static void set(Map<String, Integer> caught) {
        journal = new BugJournal(caught);
    }

    public static BugJournal get() {
        return journal;
    }
}
