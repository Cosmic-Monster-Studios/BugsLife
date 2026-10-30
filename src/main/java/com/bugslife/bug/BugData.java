package com.bugslife.bug;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.core.UUIDUtil;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;

import java.util.Optional;
import java.util.UUID;

/**
 * A captured bug, stored on a Bug Jar item and inside terrariums. A tamed pet keeps its owner through the jar, and
 * {@code age} keeps its growth or breeding cooldown (0 when unknown, e.g. jars from before it was stored).
 */
public record BugData(BugSpecies species, boolean prismatic, boolean baby, Optional<UUID> owner, int age) {
    public static final Codec<BugData> CODEC = RecordCodecBuilder.create(i -> i.group(
            BugSpecies.CODEC.fieldOf("species").forGetter(BugData::species),
            Codec.BOOL.optionalFieldOf("prismatic", false).forGetter(BugData::prismatic),
            Codec.BOOL.optionalFieldOf("baby", false).forGetter(BugData::baby),
            UUIDUtil.CODEC.optionalFieldOf("owner").forGetter(BugData::owner),
            Codec.INT.optionalFieldOf("age", 0).forGetter(BugData::age)
    ).apply(i, BugData::new));

    public static final StreamCodec<ByteBuf, BugData> STREAM_CODEC = StreamCodec.composite(
            BugSpecies.STREAM_CODEC, BugData::species,
            ByteBufCodecs.BOOL, BugData::prismatic,
            ByteBufCodecs.BOOL, BugData::baby,
            ByteBufCodecs.optional(UUIDUtil.STREAM_CODEC), BugData::owner,
            ByteBufCodecs.VAR_INT, BugData::age,
            BugData::new);

    public BugData(BugSpecies species, boolean prismatic, boolean baby) {
        this(species, prismatic, baby, Optional.empty(), 0);
    }

    public BugData(BugSpecies species, boolean prismatic, boolean baby, Optional<UUID> owner) {
        this(species, prismatic, baby, owner, 0);
    }
}
