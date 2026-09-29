package com.bugslife.client;

import com.bugslife.BugsLife;
import com.bugslife.bug.BugSpecies;
import com.bugslife.entity.BugEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.util.Color;

/** Renders any bug from its Blockbench model, with size variation, prismatic shimmer, glow and bark-clinging pose. */
public class BugRenderer extends GeoEntityRenderer<BugEntity> {
    private final BugSpecies species;

    public BugRenderer(EntityRendererProvider.Context context, BugSpecies species) {
        super(context, new DefaultedEntityGeoModel<>(BugsLife.id(species.id())));
        this.species = species;
        this.shadowRadius = species == BugSpecies.LEAF_INSECT ? 0f : Math.max(0.12f, species.width() * 0.45f);
        if (species.glows()) {
            addRenderLayer(new BugGlowLayer(this));
        }
    }

    @Override
    public void render(BugEntity bug, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource bufferSource, int packedLight) {
        // a still leaf insect is indistinguishable from foliage - unless you study it through a spyglass
        if (species == BugSpecies.LEAF_INSECT && bug.isAddedToLevel()) {
            var player = net.minecraft.client.Minecraft.getInstance().player;
            boolean still = bug.getDeltaMovement().horizontalDistanceSqr() < 1.0E-4;
            if (still && (player == null || !player.isScoping())) {
                return;
            }
        }
        super.render(bug, entityYaw, partialTick, poseStack, bufferSource, packedLight);
    }

    @Override
    public void scaleModelForRender(float widthScale, float heightScale, PoseStack poseStack, BugEntity bug, BakedGeoModel model,
                                    boolean isReRender, float partialTick, int packedLight, int packedOverlay) {
        float s = species.renderScale() * bug.getSizeScale() * (bug.isBaby() ? 0.55f : 1.0f);
        super.scaleModelForRender(widthScale * s, heightScale * s, poseStack, bug, model, isReRender, partialTick, packedLight, packedOverlay);
    }

    @Override
    protected void applyRotations(BugEntity bug, PoseStack poseStack, float ageInTicks, float rotationYaw, float partialTick, float nativeScale) {
        super.applyRotations(bug, poseStack, ageInTicks, rotationYaw, partialTick, nativeScale);
        if (bug.hasFlag(BugEntity.FLAG_HIDDEN)) {
            // buried: only the jaws show above the sand
            poseStack.translate(0, -species.height() * 0.6, 0);
        }
        Direction cling = bug.getClingFace();
        if (cling != null) {
            // stand the bug up on the bark: belly against the trunk, head pointing up
            float w = species.width();
            poseStack.translate(0, w * 0.55, -w * 0.5 / species.renderScale());
            poseStack.mulPose(Axis.XP.rotationDegrees(90));
        }
    }

    @Override
    public Color getRenderColor(BugEntity bug, float partialTick, int packedLight) {
        if (bug.isPrismatic()) {
            float hue = ((bug.tickCount + partialTick) * 0.01f + bug.getId() * 0.137f) % 1.0f;
            return Color.ofHSB(hue, 0.45f, 1.0f);
        }
        return super.getRenderColor(bug, partialTick, packedLight);
    }

    @Override
    public RenderType getRenderType(BugEntity bug, ResourceLocation texture, MultiBufferSource bufferSource, float partialTick) {
        return species.translucent() ? RenderType.entityTranslucent(texture) : RenderType.entityCutoutNoCull(texture);
    }
}
