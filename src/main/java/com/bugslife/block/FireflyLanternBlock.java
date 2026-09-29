package com.bugslife.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.state.BlockState;
import org.joml.Vector3f;

/** A lantern lit by glow goo; little firefly motes drift up out of it. */
public class FireflyLanternBlock extends LanternBlock {
    private static final DustParticleOptions MOTE = new DustParticleOptions(new Vector3f(0.85f, 1.0f, 0.35f), 0.45f);

    public FireflyLanternBlock(Properties properties) {
        super(properties);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(3) == 0) {
            double x = pos.getX() + 0.5 + (random.nextDouble() - 0.5) * 0.6;
            double y = pos.getY() + (state.getValue(HANGING) ? 0.2 : 0.1) + random.nextDouble() * 0.6;
            double z = pos.getZ() + 0.5 + (random.nextDouble() - 0.5) * 0.6;
            level.addParticle(MOTE, x, y, z, 0, 0.02, 0);
        }
    }
}
