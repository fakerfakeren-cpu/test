package com.oathbound.entity.mob;

import com.oathbound.event.GameEvents;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.RandomSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ambient.AmbientCreature;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * A soft golden moth that flutters over meadows and forests at night. Harmless; drawn to anyone carrying a lit
 * lantern, and sheds Luminous Dust when caught.
 */
public class LanternmothEntity extends AmbientCreature {
    private Vec3 goal;

    public LanternmothEntity(EntityType<? extends LanternmothEntity> type, Level level) {
        super(type, level);
        setNoGravity(true);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes().add(Attributes.MAX_HEALTH, 4.0).add(Attributes.FLYING_SPEED, 0.4);
    }

    public static boolean checkMothSpawnRules(EntityType<LanternmothEntity> type, ServerLevelAccessor level, EntitySpawnReason reason, BlockPos pos, RandomSource random) {
        if (reason == EntitySpawnReason.SPAWNER) return true;
        return pos.getY() >= level.getSeaLevel() && level.getLevel().isDarkOutside() && level.canSeeSky(pos) && random.nextInt(3) == 0;
    }

    @Override
    protected void customServerAiStep(ServerLevel level) {
        super.customServerAiStep(level);
        Player lure = null;
        if (tickCount % 20 == 0 || goal == null) {
            for (Player p : level.getEntitiesOfClass(Player.class, getBoundingBox().inflate(14))) {
                if (!GameEvents.heldLitLantern(p).isEmpty()) {
                    lure = p;
                    break;
                }
            }
            if (lure != null) {
                double a = tickCount * 0.2 + getId();
                goal = lure.getEyePosition().add(Math.cos(a) * 1.3, 0.3 + Math.sin(a * 0.7) * 0.4, Math.sin(a) * 1.3);
            } else if (goal == null || random.nextInt(8) == 0 || goal.distanceToSqr(position()) < 2) {
                goal = position().add(random.nextInt(9) - 4, random.nextInt(5) - 2, random.nextInt(9) - 4);
                int ground = level.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING, (int) goal.x, (int) goal.z);
                if (goal.y < ground + 1) goal = new Vec3(goal.x, ground + 1.5 + random.nextDouble() * 3, goal.z);
            }
        }
        Vec3 d = goal.subtract(position());
        Vec3 v = getDeltaMovement().add(Math.signum(d.x) * 0.02 - getDeltaMovement().x * 0.08, Math.signum(d.y) * 0.03 - getDeltaMovement().y * 0.1,
            Math.signum(d.z) * 0.02 - getDeltaMovement().z * 0.08);
        setDeltaMovement(v.add((random.nextDouble() - 0.5) * 0.03, (random.nextDouble() - 0.5) * 0.03, (random.nextDouble() - 0.5) * 0.03));
        float yaw = (float) (Math.atan2(v.z, v.x) * 180 / Math.PI) - 90f;
        setYRot(yaw);
        yBodyRot = yaw;
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide() && random.nextInt(3) == 0) {
            level().addParticle(ModParticles.LUMEN_MOTE.get(), getX(), getY() + 0.2, getZ(), 0, -0.01, 0);
        }
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    protected void doPush(net.minecraft.world.entity.Entity entity) {}

    @Override
    public boolean causeFallDamage(double distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected void checkFallDamage(double y, boolean onGround, BlockState state, BlockPos pos) {}

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.MOTH_FLUTTER.get();
    }

    @Override
    protected float getSoundVolume() {
        return 0.3f;
    }
}
