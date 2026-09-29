package com.bugslife.advancement;

import com.bugslife.bug.BugData;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.advancements.critereon.ContextAwarePredicate;
import net.minecraft.advancements.critereon.EntityPredicate;
import net.minecraft.advancements.critereon.SimpleCriterionTrigger;
import net.minecraft.server.level.ServerPlayer;

import java.util.Optional;

/** Fires when a player nets a bug. Filters: species id, minimum rarity, prismatic. */
public class CatchBugTrigger extends SimpleCriterionTrigger<CatchBugTrigger.Instance> {
    @Override
    public Codec<Instance> codec() {
        return Instance.CODEC;
    }

    public void trigger(ServerPlayer player, BugData bug) {
        trigger(player, inst -> inst.matches(bug));
    }

    public record Instance(Optional<ContextAwarePredicate> player, Optional<String> species, Optional<String> minRarity,
                           Optional<Boolean> prismatic) implements SimpleCriterionTrigger.SimpleInstance {
        public static final Codec<Instance> CODEC = RecordCodecBuilder.create(i -> i.group(
                EntityPredicate.ADVANCEMENT_CODEC.optionalFieldOf("player").forGetter(Instance::player),
                Codec.STRING.optionalFieldOf("species").forGetter(Instance::species),
                Codec.STRING.optionalFieldOf("min_rarity").forGetter(Instance::minRarity),
                Codec.BOOL.optionalFieldOf("prismatic").forGetter(Instance::prismatic)
        ).apply(i, Instance::new));

        boolean matches(BugData bug) {
            if (species.isPresent() && !species.get().equals(bug.species().id())) return false;
            if (prismatic.isPresent() && prismatic.get() != bug.prismatic()) return false;
            if (minRarity.isPresent()) {
                String wanted = minRarity.get();
                var rarity = bug.species().rarity();
                boolean ok = false;
                for (var r : com.bugslife.bug.BugRarity.values()) {
                    if (r.getSerializedName().equals(wanted)) {
                        ok = rarity.atLeast(r);
                    }
                }
                return ok;
            }
            return true;
        }
    }
}
