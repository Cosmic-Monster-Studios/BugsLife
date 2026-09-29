package com.bugslife.advancement;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.advancements.critereon.ContextAwarePredicate;
import net.minecraft.advancements.critereon.EntityPredicate;
import net.minecraft.advancements.critereon.SimpleCriterionTrigger;
import net.minecraft.server.level.ServerPlayer;

import java.util.Optional;

/**
 * Fires for bug-keeping actions. Actions: release, terrarium_insert, terrarium_breed, terrarium_hatch,
 * terrarium_harvest, witness_hunt, witness_pollinate, spook_mite, discover_all.
 */
public class BugActionTrigger extends SimpleCriterionTrigger<BugActionTrigger.Instance> {
    @Override
    public Codec<Instance> codec() {
        return Instance.CODEC;
    }

    public void trigger(ServerPlayer player, String action) {
        trigger(player, inst -> inst.action().map(action::equals).orElse(true));
    }

    public record Instance(Optional<ContextAwarePredicate> player, Optional<String> action) implements SimpleCriterionTrigger.SimpleInstance {
        public static final Codec<Instance> CODEC = RecordCodecBuilder.create(i -> i.group(
                EntityPredicate.ADVANCEMENT_CODEC.optionalFieldOf("player").forGetter(Instance::player),
                Codec.STRING.optionalFieldOf("action").forGetter(Instance::action)
        ).apply(i, Instance::new));
    }
}
