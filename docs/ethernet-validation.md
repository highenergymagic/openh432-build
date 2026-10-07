# Ethernet validation

Ethernet is integrated into the normal runtime using the upstream smsc911x
driver for the LAN9220. Networking, DHCP and key-authenticated SSH have been
exercised on the NAND system. A maintenance session also survived USB removal.

The factory Ethernet address is passed through the retained boot chain into
the device tree. Recovery-assisted and normal NAND boots reported the same
validated address and derived board identifier. This is not a manufacturer
serial-number implementation.

See the [Ethernet reference](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/ethernet.md)
for bus configuration, identity policy and diagnostics. Suspend/resume,
standalone supply sequencing, broad PHY interoperability and throughput
remain unqualified.

The pre-deployment candidate record remains in Git history; it must not be
used to infer that networking is absent from the normal runtime.
