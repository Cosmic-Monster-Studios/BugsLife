package com.bugslife.bug;

import com.bugslife.network.Network;
import com.bugslife.registry.ModAttachments;
import com.bugslife.registry.ModTriggers;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;

public final class JournalEvents {
    private JournalEvents() {
    }

    @SubscribeEvent
    public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            Network.syncJournal(player);
        }
    }

    @SubscribeEvent
    public static void onRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            Network.syncJournal(player);
        }
    }

    /** Records a catch, announces rare finds, fires advancements and syncs the Field Guide. */
    public static void recordCatch(ServerPlayer player, BugData bug) {
        BugJournal journal = player.getData(ModAttachments.JOURNAL);
        boolean first = journal.record(bug.species());
        player.setData(ModAttachments.JOURNAL, journal);
        ModTriggers.CATCH_BUG.get().trigger(player, bug);

        BugRarity rarity = bug.species().rarity();
        Component name = bug.species().displayName().copy().withStyle(rarity.color);
        if (bug.prismatic()) {
            player.sendSystemMessage(Component.translatable("bugslife.msg.caught_prismatic", name).withStyle(ChatFormatting.LIGHT_PURPLE));
            player.playNotifySound(SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.PLAYERS, 1f, 1.2f);
        } else if (rarity.atLeast(BugRarity.RARE)) {
            player.sendSystemMessage(Component.translatable("bugslife.msg.caught_rare", rarity.displayName(), name));
            player.playNotifySound(rarity == BugRarity.LEGENDARY ? SoundEvents.UI_TOAST_CHALLENGE_COMPLETE : SoundEvents.PLAYER_LEVELUP,
                    SoundSource.PLAYERS, 0.8f, 1.4f);
        }
        if (first) {
            player.displayClientMessage(Component.translatable("bugslife.msg.new_entry", name, journal.discovered(),
                    BugSpecies.values().length).withStyle(ChatFormatting.YELLOW), true);
            int found = journal.discovered();
            if (found >= 5) ModTriggers.BUG_ACTION.get().trigger(player, "discover_5");
            if (found >= 10) ModTriggers.BUG_ACTION.get().trigger(player, "discover_10");
            if (found >= 25) ModTriggers.BUG_ACTION.get().trigger(player, "discover_25");
            if (found >= 50) ModTriggers.BUG_ACTION.get().trigger(player, "discover_50");
            if (found == BugSpecies.values().length) ModTriggers.BUG_ACTION.get().trigger(player, "discover_all");
        }
        Network.syncJournal(player);
    }
}
