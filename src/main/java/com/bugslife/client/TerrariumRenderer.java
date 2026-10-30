package com.bugslife.client;

import com.bugslife.block.TerrariumBlockEntity;
import com.bugslife.bug.BugData;
import com.bugslife.bug.BugSpecies;
import com.bugslife.bug.Movement;
import com.bugslife.entity.BugEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.entity.EntityRenderDispatcher;
import net.minecraft.util.Mth;
import net.minecraft.world.level.Level;

import java.util.ArrayList;
import java.util.List;

/** Draws the living, animated bugs inside a terrarium. */
public class TerrariumRenderer implements BlockEntityRenderer<TerrariumBlockEntity> {
    private static final double[][] SLOTS = {{0.32, 0.3}, {0.68, 0.7}, {0.7, 0.32}, {0.3, 0.68}, {0.5, 0.2}, {0.5, 0.8}, {0.2, 0.5}, {0.8, 0.5}};

    public TerrariumRenderer(BlockEntityRendererProvider.Context context) {
    }

    @Override
    public void render(TerrariumBlockEntity be, float partialTick, PoseStack poseStack, MultiBufferSource buffer, int packedLight, int packedOverlay) {
        Level level = be.getLevel();
        if (level == null) return;
        List<BugData> bugs = be.bugs();
        if (be.renderBugs == null || be.renderBugs.size() != bugs.size() || needsRebuild(be, bugs)) {
            List<BugEntity> list = new ArrayList<>();
            for (BugData data : bugs) {
                BugEntity bug = BugEntity.fromData(level, data);
                if (bug != null) {
                    bug.setPrismatic(data.prismatic());
                    list.add(bug);
                }
            }
            be.renderBugs = list;
        }
        EntityRenderDispatcher dispatcher = Minecraft.getInstance().getEntityRenderDispatcher();
        long time = level.getGameTime();
        dispatcher.setRenderShadow(false);
        for (int i = 0; i < be.renderBugs.size(); i++) {
            BugEntity bug = be.renderBugs.get(i);
            BugSpecies s = bug.species();
            bug.tickCount = (int) time + i * 37;
            float t = time + partialTick + i * 50;
            float yaw = (t * 0.4f + i * 97) % 360f;
            bug.setYRot(yaw);
            bug.yBodyRot = bug.yBodyRotO = yaw;
            bug.yHeadRot = bug.yHeadRotO = yaw;
            bug.setOnGround(!s.flies());

            float scale = Math.min(0.7f, 0.26f / Math.max(0.25f, s.width()));
            double x = SLOTS[i % SLOTS.length][0];
            double z = SLOTS[i % SLOTS.length][1];
            double y = 0.13;
            if (s.movement() == Movement.HANG) {
                x = z = 0.5;
                y = 0.94 - s.height() * scale;
            } else if (s.flies()) {
                y = 0.35 + 0.08 * Mth.sin(t * 0.08f);
                x = 0.5 + 0.18 * Mth.cos(t * 0.03f + i);
                z = 0.5 + 0.18 * Mth.sin(t * 0.03f + i);
            }
            poseStack.pushPose();
            poseStack.translate(x, y, z);
            poseStack.scale(scale, scale, scale);
            dispatcher.render(bug, 0, 0, 0, yaw, partialTick, poseStack, buffer, packedLight);
            poseStack.popPose();
        }
        dispatcher.setRenderShadow(true);
    }

    private static boolean needsRebuild(TerrariumBlockEntity be, List<BugData> bugs) {
        for (int i = 0; i < bugs.size(); i++) {
            BugEntity e = be.renderBugs.get(i);
            BugData d = bugs.get(i);
            if (e.species() != d.species() || e.isPrismatic() != d.prismatic() || e.isBaby() != d.baby()) return true;
        }
        return false;
    }
}
