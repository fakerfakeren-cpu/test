package com.oathbound.entity.mob;

/** A creature drawn by the shared fauna renderer: it reports one special action and a variant to its model. */
public interface FaunaEntity {
    default boolean fauna$action() {
        return false;
    }

    default int fauna$variant() {
        return 0;
    }

    /** Drawn half-transparent (stalking, phasing). */
    default boolean fauna$ghost() {
        return false;
    }
}
