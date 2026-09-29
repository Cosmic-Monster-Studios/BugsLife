package com.bugslife.bug;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;

/** A captured bug, stored on a Bug Jar item and inside terrariums. */
public record BugData(BugSpecies species, boolean prismatic, boolean baby) {
    public static final Codec<BugData> CODEC = RecordCodecBuilder.create(i -> i.group(
            BugSpecies.CODEC.fieldOf("species").forGetter(BugData::species),
            Codec.BOOL.optionalFieldOf("prismatic", false).forGetter(BugData::prismatic),
            Codec.BOOL.optionalFieldOf("baby", false).forGetter(BugData::baby)
    ).apply(i, BugData::new));

    public static final StreamCodec<ByteBuf, BugData> STREAM_CODEC = StreamCodec.composite(
            BugSpecies.STREAM_CODEC, BugData::species,
            ByteBufCodecs.BOOL, BugData::prismatic,
            ByteBufCodecs.BOOL, BugData::baby,
            BugData::new);
}
