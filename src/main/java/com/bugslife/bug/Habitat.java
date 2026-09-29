package com.bugslife.bug;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import org.jetbrains.annotations.Nullable;

/** Decides where (if anywhere) a bug can appear near a random sample point. */
@FunctionalInterface
public interface Habitat {
    /**
     * @param origin a random point near a player
     * @return the block position the bug should spawn in, or null if this spot is unsuitable
     */
    @Nullable
    BlockPos find(ServerLevel level, BlockPos origin, RandomSource random);
}
