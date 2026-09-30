package com.oathbound.entity.mob;

import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.tags.ItemTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.equine.AbstractHorse;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * A grown stag of the glimmer herds, and a mount for a knight: tame it like a horse (patience and apples, or
 * moonpetals, which it loves), saddle it and ride. It is quick, jumps high, and at a gallop its antlers leave a trail
 * of moonlight.
 */
public class GlimmerstagEntity extends AbstractHorse implements FaunaEntity {
    public GlimmerstagEntity(EntityType<? extends GlimmerstagEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createBaseHorseAttributes().add(Attributes.MAX_HEALTH, 30.0).add(Attributes.MOVEMENT_SPEED, 0.3).add(Attributes.JUMP_STRENGTH, 0.9);
    }

    @Override
    protected void randomizeAttributes(RandomSource r) {
        var hp = getAttribute(Attributes.MAX_HEALTH);
        if (hp != null) hp.setBaseValue(26 + r.nextInt(11));
        var speed = getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed != null) speed.setBaseValue(0.28 + r.nextDouble() * 0.07);
        var jump = getAttribute(Attributes.JUMP_STRENGTH);
        if (jump != null) jump.setBaseValue(0.8 + r.nextDouble() * 0.25);
    }

    /** Variant 1 once it wears a saddle: the model shows it. */
    @Override
    public int fauna$variant() {
        return getItemBySlot(EquipmentSlot.SADDLE).isEmpty() ? 0 : 1;
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return stack.is(ItemTags.HORSE_FOOD) || stack.is(ModBlocks.MOONPETAL.get().asItem());
    }

    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob other) {
        return ModEntities.GLIMMERSTAG.get().create(level, EntitySpawnReason.BREEDING);
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (!level().isClientSide()) return;
        boolean galloping = isVehicle() && getDeltaMovement().horizontalDistanceSqr() > 0.04;
        if (galloping || random.nextInt(level().isDarkOutside() ? 6 : 40) == 0) {
            // moonlight from the antler tips
            level().addParticle(galloping ? ModParticles.LUMEN_MOTE.get() : ModParticles.FIREFLY.get(),
                getRandomX(0.6), getY() + getBbHeight() + 0.4 + random.nextDouble() * 0.6, getRandomZ(0.6), 0, 0.01, 0);
        }
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.FAWN_CALL.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.FAWN_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.FAWN_HURT.get();
    }

    @Override
    public float getVoicePitch() {
        return 0.8f;
    }
}
