package com.bugslife.gametest;

import com.bugslife.block.TerrariumBlockEntity;
import com.bugslife.bug.BugSpecies;
import com.bugslife.entity.BugEntity;
import com.bugslife.entity.goal.SpinWebGoal;
import com.bugslife.item.BugJarItem;
import com.bugslife.item.BugNetItem;
import com.bugslife.registry.ModBlocks;
import com.bugslife.registry.ModEntities;
import com.bugslife.registry.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;
import net.neoforged.neoforge.items.ItemStackHandler;

/** Server regressions. Only loaded by the dedicated gameTestServer source binding. */
@GameTestHolder("bugslife")
@PrefixGameTestTemplate(false)
public final class RegressionGameTests {
    @BeforeBatch(batch = "bugslife_regressions")
    public static void report(ServerLevel level) {
        try {
            GlobalTestReporter.replaceWith(new JUnitLikeTestReporter(new java.io.File(
                    System.getProperty("bugslife.tests.report"))));
        } catch (javax.xml.parsers.ParserConfigurationException failure) {
            throw new IllegalStateException(failure);
        }
    }

    private static ServerPlayer player(GameTestHelper helper, boolean full) {
        ServerPlayer player = new net.neoforged.neoforge.common.util.FakePlayer(helper.getLevel(),
                new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(), "RegressionPlayer"));
        player.setGameMode(GameType.CREATIVE);
        BlockPos origin = helper.absolutePos(new BlockPos(3, 1, 3));
        player.moveTo(origin.getX() + .5, origin.getY(), origin.getZ() + .5, 0, 0);
        player.setYHeadRot(0);
        player.yHeadRotO = 0;
        if (full) for (int slot = 0; slot < player.getInventory().items.size(); slot++)
            player.getInventory().items.set(slot, new ItemStack(Items.STONE, 64));
        return player;
    }

    private static int dropped(GameTestHelper helper, ServerPlayer player, net.minecraft.world.item.Item item) {
        return helper.getLevel().getEntitiesOfClass(ItemEntity.class, player.getBoundingBox().inflate(4))
                .stream().filter(entity -> entity.getItem().is(item)).mapToInt(entity -> entity.getItem().getCount()).sum();
    }

    private static TerrariumBlockEntity output(GameTestHelper helper, int count) {
        BlockPos relative = new BlockPos(1, 1, 1);
        helper.setBlock(relative, ModBlocks.TERRARIUM.get());
        TerrariumBlockEntity terrarium = (TerrariumBlockEntity) helper.getLevel().getBlockEntity(helper.absolutePos(relative));
        ItemStackHandler items = new ItemStackHandler(9);
        items.setStackInSlot(0, new ItemStack(ModItems.FRASS.get(), count));
        CompoundTag saved = new CompoundTag();
        saved.put("Output", items.serializeNBT(helper.getLevel().registryAccess()));
        terrarium.loadWithComponents(saved, helper.getLevel().registryAccess());
        return terrarium;
    }

    @GameTest(template = "empty", batch = "bugslife_regressions", timeoutTicks = 30)
    public static void creativeHarvestOverflowConservesItems(GameTestHelper helper) {
        ServerPlayer player = player(helper, true);
        TerrariumBlockEntity terrarium = output(helper, 17);
        terrarium.collect(player);
        helper.assertTrue(dropped(helper, player, ModItems.FRASS.get()) == 17,
                "A full creative inventory must drop all 17 harvested items instead of deleting them");
        helper.assertTrue(terrarium.getOutputHandler().getStackInSlot(0).isEmpty(), "Collected output must be drained once");
        terrarium.collect(player);
        helper.assertTrue(dropped(helper, player, ModItems.FRASS.get()) == 17, "Repeated harvest must not duplicate overflow");
        helper.succeed();
    }

    @GameTest(template = "empty", batch = "bugslife_regressions", timeoutTicks = 30)
    public static void creativeHarvestMergesThenDropsRemainder(GameTestHelper helper) {
        ServerPlayer player = player(helper, true);
        player.getInventory().items.set(0, new ItemStack(ModItems.FRASS.get(), 60));
        output(helper, 17).collect(player);
        helper.assertTrue(player.getInventory().items.get(0).getCount() == 64, "Existing stack must receive four items");
        helper.assertTrue(dropped(helper, player, ModItems.FRASS.get()) == 13, "Only the 13-item remainder should drop");
        helper.succeed();
    }

    private static BugEntity bug(GameTestHelper helper, BugSpecies species, double x, double y, double z) {
        BugEntity bug = ModEntities.get(species).get().create(helper.getLevel());
        BlockPos origin = helper.absolutePos(BlockPos.ZERO);
        bug.moveTo(origin.getX() + x, origin.getY() + y, origin.getZ() + z, 0, 0);
        helper.getLevel().addFreshEntity(bug);
        return bug;
    }

    @GameTest(template = "empty", batch = "bugslife_regressions", timeoutTicks = 30)
    public static void creativeCaptureFullInventoryConservesBug(GameTestHelper helper) {
        ServerPlayer player = player(helper, true);
        ItemStack net = new ItemStack(ModItems.SILK_NET.get());
        player.setItemInHand(InteractionHand.MAIN_HAND, net);
        BugEntity ladybug = bug(helper, BugSpecies.LADYBUG, 3.5, 1, 4.5);
        ModItems.SILK_NET.get().interactLivingEntity(net, player, ladybug, InteractionHand.MAIN_HAND);
        helper.assertTrue(ladybug.isRemoved(), "A common ladybug must be caught with the guaranteed silk-net chance");
        var jars = helper.getLevel().getEntitiesOfClass(ItemEntity.class, player.getBoundingBox().inflate(4))
                .stream().filter(entity -> BugJarItem.getBug(entity.getItem()) != null).toList();
        helper.assertTrue(jars.size() == 1 && BugJarItem.getBug(jars.get(0).getItem()).species() == BugSpecies.LADYBUG,
                "The caught bug must survive as exactly one filled jar when creative inventory is full");
        helper.succeed();
    }

    @GameTest(template = "empty", batch = "bugslife_regressions", timeoutTicks = 30)
    public static void netAssistRejectsColliderButKeepsVisibleNearMiss(GameTestHelper helper) {
        ServerPlayer player = player(helper, false);
        // LivingEntity's constructor randomizes head yaw; moveTo sets body yaw only.
        player.setYHeadRot(0);
        player.yHeadRotO = 0;
        double eye = player.getEyeY() - helper.absolutePos(BlockPos.ZERO).getY();
        BugEntity ladybug = bug(helper, BugSpecies.LADYBUG, 3.75, eye - .1, 5.5);
        BlockPos panePosition = helper.absolutePos(new BlockPos(3, 2, 4));
        var originalPane = helper.getLevel().getBlockState(panePosition);
        try {
            assertNetIsolation(helper, player, ladybug);
            helper.assertTrue(BugNetItem.nearMiss(player) == ladybug, "A visible 0.25-block near miss must remain assisted");
            ladybug.moveTo(helper.absolutePos(new BlockPos(3, 1, 4)).getX() + .5,
                    player.getEyeY() - .1, helper.absolutePos(new BlockPos(3, 1, 4)).getZ() + .75);
            helper.setBlock(new BlockPos(3, 2, 4), Blocks.GLASS_PANE);
            assertNetIsolation(helper, player, ladybug);
            var targetPoint = new net.minecraft.world.phys.Vec3(player.getX(), player.getEyeY(), ladybug.getBoundingBox().minZ);
            var collider = helper.getLevel().clip(new net.minecraft.world.level.ClipContext(player.getEyePosition(), targetPoint,
                    net.minecraft.world.level.ClipContext.Block.COLLIDER, net.minecraft.world.level.ClipContext.Fluid.NONE, player));
            String geometry = " eye=" + player.getEyePosition() + " body=" + ladybug.getBoundingBox() + " target=" + targetPoint
                    + " pane=" + panePosition + ":" + helper.getLevel().getBlockState(panePosition)
                    + " clip=" + collider.getType() + ":" + collider.getLocation()
                    + " headYaw=" + player.getYHeadRot() + " view=" + player.getViewVector(1.0f);
            helper.assertTrue(collider.getType() == net.minecraft.world.phys.HitResult.Type.BLOCK,
                    "Pane fixture must obstruct the actual body centerline before the net assertion" + geometry);
            BugEntity candidate = BugNetItem.nearMiss(player);
            String returned = candidate == null ? "null" : candidate.species() + ":" + candidate.getUUID() + ":" + candidate.position();
            System.out.println("[BugsLife net regression]" + geometry + " returned=" + returned);
            helper.assertTrue(candidate == null, "Aim-assist inflation must not reach through a collider" + geometry + " returned=" + returned);
            ladybug.moveTo(helper.absolutePos(new BlockPos(3, 1, 4)).getX() + .9,
                    player.getEyeY() - .1, helper.absolutePos(new BlockPos(3, 1, 4)).getZ() + .75);
            assertNetIsolation(helper, player, ladybug);
            helper.assertTrue(BugNetItem.nearMiss(player) == ladybug,
                    "An actual body edge exposed beside the pane must still receive near-miss assistance");
            helper.succeed();
        } finally {
            ladybug.discard();
            helper.getLevel().setBlockAndUpdate(panePosition, originalPane);
        }
    }

    private static void assertNetIsolation(GameTestHelper helper, ServerPlayer player, BugEntity seeded) {
        var eye = player.getEyePosition();
        var end = eye.add(player.getViewVector(1.0f).scale(player.entityInteractionRange() + BugNetItem.AIM_ASSIST));
        var candidates = helper.getLevel().getEntitiesOfClass(BugEntity.class,
                new AABB(eye, end).inflate(BugNetItem.AIM_ASSIST + 1.0), BugEntity::isAlive);
        helper.assertTrue(candidates.size() == 1 && candidates.get(0) == seeded,
                "Net fixture must contain only the seeded bug in its candidate region; found="
                + candidates.stream().map(bug -> bug.species() + ":" + bug.getUUID() + ":" + bug.position()).toList());
    }
    private static SpinWebGoal pending(BugEntity spider, BlockPos target) {
        SpinWebGoal goal = new SpinWebGoal(spider);
        // Set up a previously selected site deterministically; production world-write logic remains under test.
        try {
            var field = SpinWebGoal.class.getDeclaredField("spot");
            field.setAccessible(true);
            field.set(goal, target);
        } catch (ReflectiveOperationException failure) { throw new IllegalStateException(failure); }
        goal.start();
        return goal;
    }

    @GameTest(template = "empty", batch = "bugslife_regressions", timeoutTicks = 30)
    public static void webPolicyFlipPreventsPendingWrite(GameTestHelper helper) {
        ServerLevel level = helper.getLevel();
        boolean original = level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING);
        try {
            level.getGameRules().getRule(GameRules.RULE_MOBGRIEFING).set(true, level.getServer());
            BugEntity spider = bug(helper, BugSpecies.ORB_WEAVER, 3.5, 2, 3.5);
            BlockPos target = helper.absolutePos(new BlockPos(3, 2, 3));
            helper.setBlock(new BlockPos(4, 2, 3), Blocks.OAK_LOG);
            helper.assertTrue(level.getBlockState(target).isAir(), "Pending web fixture target must start as air: " + level.getBlockState(target));
            SpinWebGoal goal = pending(spider, target);
            level.getGameRules().getRule(GameRules.RULE_MOBGRIEFING).set(false, level.getServer());
            goal.tick();
            helper.assertTrue(level.getBlockState(target).isAir(), "A policy disabled after selection must prevent the pending web write");
            level.getGameRules().getRule(GameRules.RULE_MOBGRIEFING).set(true, level.getServer());
            pending(spider, target).tick();
            helper.assertTrue(level.getBlockState(target).is(Blocks.COBWEB), "The same supported site must permit a web with policy enabled");
            helper.succeed();
        } finally { level.getGameRules().getRule(GameRules.RULE_MOBGRIEFING).set(original, level.getServer()); }
    }

    @GameTest(template = "empty", batch = "bugslife_regressions", timeoutTicks = 30)
    public static void racingWebGoalsRespectWriteTimeCap(GameTestHelper helper) {
        ServerLevel level = helper.getLevel();
        boolean original = level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING);
        try {
            level.getGameRules().getRule(GameRules.RULE_MOBGRIEFING).set(true, level.getServer());
            helper.setBlock(new BlockPos(1, 2, 1), Blocks.COBWEB);
            BugEntity first = bug(helper, BugSpecies.ORB_WEAVER, 3.5, 2, 3.5);
            BugEntity second = bug(helper, BugSpecies.ORB_WEAVER, 3.5, 2, 4.5);
            helper.setBlock(new BlockPos(4, 2, 3), Blocks.OAK_LOG);
            helper.setBlock(new BlockPos(4, 2, 4), Blocks.OAK_LOG);
            BlockPos a = helper.absolutePos(new BlockPos(3, 2, 3));
            BlockPos b = helper.absolutePos(new BlockPos(3, 2, 4));
            SpinWebGoal firstGoal = pending(first, a), secondGoal = pending(second, b);
            helper.assertTrue(level.getBlockState(a).isAir() && level.getBlockState(b).isAir(),
                    "Both pending web sites must start as air: " + level.getBlockState(a) + " / " + level.getBlockState(b));
            firstGoal.tick();
            secondGoal.tick();
            helper.assertTrue(level.getBlockState(a).is(Blocks.COBWEB), "First pending goal should place the second local web");
            helper.assertTrue(level.getBlockState(b).isAir(), "Second pending goal must observe the newly reached two-web cap");
            helper.succeed();
        } finally { level.getGameRules().getRule(GameRules.RULE_MOBGRIEFING).set(original, level.getServer()); }
    }

    @GameTest(template = "empty", batch = "bugslife_regressions", timeoutTicks = 30)
    public static void ceilingRemovalCancelsCourtship(GameTestHelper helper) {
        helper.setBlock(new BlockPos(3, 4, 3), Blocks.STONE);
        helper.setBlock(new BlockPos(4, 4, 3), Blocks.STONE);
        BugEntity first = bug(helper, BugSpecies.GLOWWORM, 3.5, 2, 3.5);
        BugEntity second = bug(helper, BugSpecies.GLOWWORM, 4.5, 2, 3.5);
        first.attachToCeiling(); second.attachToCeiling();
        helper.assertTrue(first.isNoGravity() && second.isNoGravity(), "Fixture adults must attach before courtship: "
                + first.position() + " / " + second.position());
        first.setInLove(null); second.setInLove(null);
        var courtship = new com.bugslife.entity.goal.HangingBreedGoal(first);
        helper.assertTrue(courtship.canUse(), "A nearby attached same-species pair must begin courtship");
        helper.setBlock(new BlockPos(4, 4, 3), Blocks.AIR);
        helper.assertTrue(!courtship.canContinueToUse(), "Losing either ceiling must cancel a pending courtship: first="
                + first.position() + " second=" + second.position() + " ceiling="
                + helper.getLevel().getBlockState(helper.absolutePos(new BlockPos(4, 4, 3))));
        for (int tick = 0; tick < 100; tick++) courtship.tick();
        helper.assertTrue(helper.getLevel().getEntitiesOfClass(BugEntity.class, first.getBoundingBox().inflate(4),
                bug -> bug.species() == BugSpecies.GLOWWORM && bug.isBaby()).isEmpty(),
                "Cancelled courtship must not produce a detached baby");
        helper.succeed();
    }
    @GameTest(template = "empty", batch = "bugslife_regressions", timeoutTicks = 200)
    public static void groundedGlowwormsAttachAndBreedDespiteFallingMotion(GameTestHelper helper) {
        for (int x = 2; x <= 5; x++) for (int z = 2; z <= 5; z++) {
            helper.setBlock(new BlockPos(x, -1, z), Blocks.STONE);
            helper.setBlock(new BlockPos(x, 2, z), Blocks.STONE);
        }
        BugEntity first = bug(helper, BugSpecies.GLOWWORM, 3.5, 0, 3.5);
        BugEntity second = bug(helper, BugSpecies.GLOWWORM, 4.5, 0, 3.5);
        first.setDeltaMovement(0, -.0784, 0);
        second.setDeltaMovement(0, -.0784, 0);
        first.setInLove(null); second.setInLove(null);
        // No direct attach/no-gravity call: exercise registered server AI from grounded placement.
        AABB region = first.getBoundingBox().inflate(4);
        helper.runAfterDelay(140, () -> {
            var children = helper.getLevel().getEntitiesOfClass(BugEntity.class, region,
                    bug -> bug.species() == BugSpecies.GLOWWORM && bug.isBaby());
            helper.assertTrue(children.size() == 1, "Grounded falling parents must auto-attach and produce exactly one baby; first="
                    + first.position() + " gravity=" + first.isNoGravity() + " second=" + second.position()
                    + " gravity=" + second.isNoGravity() + " babies=" + children.size());
            helper.assertTrue(first.isNoGravity() && second.isNoGravity() && children.get(0).isNoGravity(),
                    "Grounded attachment must remain stable through courtship and offspring placement");
            helper.succeed();
        });
    }
    @GameTest(template = "empty", batch = "bugslife_regressions", timeoutTicks = 150)
    public static void attachedGlowwormsBreedAndAttachOffspring(GameTestHelper helper) {
        for (int x = 2; x <= 5; x++) for (int z = 2; z <= 5; z++)
            helper.setBlock(new BlockPos(x, 4, z), Blocks.STONE);
        BugEntity first = bug(helper, BugSpecies.GLOWWORM, 3.5, 2, 3.5);
        BugEntity second = bug(helper, BugSpecies.GLOWWORM, 4.5, 2, 3.5);
        first.attachToCeiling(); second.attachToCeiling();
        helper.assertTrue(first.isNoGravity() && second.isNoGravity(), "Fixture adults must attach before courtship: "
                + first.position() + " / " + second.position());
        first.setInLove(null); second.setInLove(null);
        AABB region = first.getBoundingBox().inflate(4);
        helper.runAfterDelay(100, () -> {
            var children = helper.getLevel().getEntitiesOfClass(BugEntity.class, region,
                    bug -> bug.species() == BugSpecies.GLOWWORM && bug.isBaby());
            helper.assertTrue(children.size() == 1, "Adjacent attached adult glowworms must produce exactly one offspring");
            helper.assertTrue(first.isNoGravity() && second.isNoGravity() && children.get(0).isNoGravity(),
                    "Parents and newborn must remain attached to the ceiling");
            BugEntity child = children.get(0);
            child.setAge(-1);
            helper.runAfterDelay(3, () -> {
                double underside = helper.absolutePos(new BlockPos(3, 4, 3)).getY();
                helper.assertTrue(!child.isBaby() && child.isNoGravity(), "A growing child must remain ceiling attached");
                helper.assertTrue(Math.abs(child.getBoundingBox().maxY - (underside - .01)) < .03,
                        "Growth must reposition the larger body below the ceiling without embedding it");
                helper.succeed();
            });
        });
    }
}
