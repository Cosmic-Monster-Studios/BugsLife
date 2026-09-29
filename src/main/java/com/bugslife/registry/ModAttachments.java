package com.bugslife.registry;

import com.bugslife.BugsLife;
import com.bugslife.bug.BugJournal;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

import java.util.function.Supplier;

public final class ModAttachments {
    public static final DeferredRegister<AttachmentType<?>> ATTACHMENTS = DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, BugsLife.MODID);

    public static final Supplier<AttachmentType<BugJournal>> JOURNAL = ATTACHMENTS.register("journal",
            () -> AttachmentType.builder(() -> new BugJournal()).serialize(BugJournal.CODEC).copyOnDeath().build());

    private ModAttachments() {
    }
}
