package com.bugslife.network;

import com.bugslife.BugsLife;
import com.bugslife.bug.BugJournal;
import com.bugslife.registry.ModAttachments;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;

import java.util.HashMap;
import java.util.Map;

public final class Network {
    private Network() {
    }

    /** Server -> client: the player's bug journal, for the Field Guide. */
    public record JournalSync(Map<String, Integer> caught) implements CustomPacketPayload {
        public static final Type<JournalSync> TYPE = new Type<>(BugsLife.id("journal"));
        public static final StreamCodec<RegistryFriendlyByteBuf, JournalSync> STREAM_CODEC = StreamCodec.composite(
                ByteBufCodecs.map(HashMap::new, ByteBufCodecs.STRING_UTF8, ByteBufCodecs.VAR_INT), JournalSync::caught,
                JournalSync::new);

        @Override
        public Type<? extends CustomPacketPayload> type() {
            return TYPE;
        }
    }

    public static void register(RegisterPayloadHandlersEvent event) {
        event.registrar("1").playToClient(JournalSync.TYPE, JournalSync.STREAM_CODEC,
                (payload, ctx) -> ctx.enqueueWork(() -> ClientJournal.set(payload.caught())));
    }

    public static void syncJournal(ServerPlayer player) {
        BugJournal journal = player.getData(ModAttachments.JOURNAL);
        PacketDistributor.sendToPlayer(player, new JournalSync(new HashMap<>(journal.asMap())));
    }
}
