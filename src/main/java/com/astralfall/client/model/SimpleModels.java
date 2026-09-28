package com.astralfall.client.model;

import com.astralfall.client.render.States;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;

/** Models for the non-living entities (meteor, singularity). */
public final class SimpleModels {
    private SimpleModels() {}

    public static class Meteor extends EntityModel<States.Meteor> {
        public Meteor(ModelPart root) {
            super(root);
        }
    }

    /** Renders either the black core or the glowing accretion disk of a singularity. */
    public static class Singularity extends EntityModel<States.Singularity> {
        private final ModelPart core, disk;
        private final boolean diskOnly;

        public Singularity(ModelPart root, boolean diskOnly) {
            super(root);
            this.core = root.getChild("core");
            this.disk = root.getChild("disk");
            this.diskOnly = diskOnly;
        }

        @Override
        public void setupAnim(States.Singularity s) {
            super.setupAnim(s);
            core.visible = !diskOnly;
            disk.visible = diskOnly;
            disk.yRot = s.ageInTicks * 0.25f;
            disk.xRot = 0.35f;
            core.yRot = s.ageInTicks * 0.05f;
        }
    }
}
