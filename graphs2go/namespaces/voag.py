from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class VOAG(DefinedNamespace):
    """
    W.I.P. testing importing of concepts from other models

    Created by Ralph Hodgson
    """

    _NS = Namespace("http://voag.linkedmodel.org/voag/")
    _SCHEMA = Namespace("http://voag.linkedmodel.org/2.0/schema/voag")
    _REFDATA = Namespace("http://voag.linkedmodel.org/2.0/refdata/voag")

    _fail = True

    Accreditation: URIRef  #
    Attribution: URIRef  # specifies how credit should be given when citing the creators of a piece of work. Attribution must use the specified attribution text and optionally use logos that are provided in the attribution details below., with the names of points of contact
    ChangeFrequency: URIRef  #
    CreativeCommonsWork: URIRef  # A potentially copyrightable work
    withAttributionTo: URIRef  #  A property that is either used to hold a string or a reference to an instance of "voag:Attribution", from the VOAG ontology
    Never: URIRef  # A "ChangeFrequency"
    Daily: URIRef  # A "ChangeFrequency"
    Weekly: URIRef  # A "ChangeFrequency"
    BiWeekly: URIRef  # A "ChangeFrequency"
    Monthly: URIRef  # A "ChangeFrequency"
    BiMonthly: URIRef  # A "ChangeFrequency"
    Quarterly: URIRef  # A "ChangeFrequency"
    BiQuarterly: URIRef  # A "ChangeFrequency"
    Annually: URIRef  # A "ChangeFrequency"
    OnDemand: URIRef  # A "ChangeFrequency"
    UncertainFrequency: URIRef  # A "ChangeFrequency"

    ACADEMIC_FREE_LICENSE = URIRef(_NS["ACADEMIC-FREE-LICENSE"])
    # "ACADEMIC_FREE_LICENSE" is a free software license, not copyleft, and incompatible with the GNU GPL.
    # Some versions contain contract clauses similar to the Open Software License
    ACDL_V1PT0 = URIRef(_NS["ACDL-V1PT0"])
    # A Free Documentation license that is incompatible with the GNU FDL
    AGPL_V1PT0 = URIRef(_NS["AGPL-V1PT0"])
    # A free software license, copyleft, and incompatible with the GNU GPL.
    # It consists of the GNU GPL version 2, with one additional section that Affero added with FSF approval.
    # The new section, 2(d), covers the distribution of application programs through web services or computer networks.
    # This license has been succeeded by the GNU Affero General Public License version 3; please use that instead.
    AGPL_V3PT0 = URIRef(_NS["AGPL-V3PT0"])
    # A free software, copyleft license. Its terms effectively consist of the terms of GPLv3, with an additional
    # paragraph in section 13 to allow users who interact with the licensed software over a network to receive
    # the source for that program.
    # GNU AGPL v3.0 should be considered by Developers considering using the GNU AGPL for any software which
    # will commonly be run over a network. Note that the GNU AGPL is not compatible with GPLv2.
    # It is also technically not compatible with GPLv3 in a strict sense: you cannot take code released under
    # the GNU AGPL and convey or modify it however you like under the terms of GPLv3, or vice versa.
    # However, you are allowed to combine separate modules or source files released under both of those licenses
    # in a single project, which will provide many programmers with all the permission they need to make the
    # programs they want.
    APACHE_V1PT0 = URIRef(_NS["APACHE-V1PT0"])
    # A simple, permissive non-copyleft free software license with an advertising clause.
    # This creates practical problems like those of the original BSD license, including incompatibility with
    # the GNU GPL
    APACHE_V1PT1 = URIRef(_NS["APACHE-V1PT1"])
    # A permissive non-copyleft free software license. It has a few requirements that render it incompatible with
    # the GNU GPL, such as strong prohibitions on the use of Apache-related names
    APACHE_V2PT0 = URIRef(_NS["APACHE-V2PT0"])
    # Apache License, Version 2.0
    APSL_V1PT0 = URIRef(_NS["APSL-V1PT0"])
    # Apple's Common Documentation License, Version 1.0. A free software license, incompatible with the GNU GPL.
    # We recommend that you not use this license for new software that you write, but it is ok to use and improve
    # the software released under this license
    APSL_V1PTX = URIRef(_NS["APSL-V1PTX"])
    # Apple Public Source License (APSL), version 1.x. Versions 1.0, 1.1 and 1.2 are not free software licenses
    # Please don't use these licenses, and we urge you to avoid any software that has been released under them.
    # Version 2.0 of the APSL is a free software license
    APSL_V2 = URIRef(_NS["APSL-V2"])
    #  voag:incompatibleWith voag:GNU-GPL-V3 ;
    ARPHIC_PUBLIC_LICENSE = URIRef(_NS["ARPHIC-PUBLIC-LICENSE"])
    # A copyleft free software license, incompatible with the GPL. Its normal use is for fonts, and in that use,
    # the incompatibility does not cause a problem
    BERKELEY_DATABASE_LICENSE = URIRef(_NS["BERKELEY-DATABASE-LICENSE"])
    # A free software license, compatible with the GNU GPL.
    # It is also known as the "Sleepycat Software Product License"
    BITTORRENT_LICENSE = URIRef(_NS["BITTORRENT-LICENSE"])
    # A free software license, but incompatible with the GPL, for the same reasons as the Jabber Open Source
    # License
    BOOST_LICENSE = URIRef(_NS["BOOST-LICENSE"])
    # A simple, permissive non-copyleft free software license, compatible with the GNU GPL
    BSD_ORIGINAL_LICENSE = URIRef(_NS["BSD-ORIGINAL-LICENSE"])
    # A simple, permissive non-copyleft free software license with a serious flaw: the “obnoxious BSD advertising clause”.
    # The flaw is not fatal; that is, it does not render the software non-free.
    # But it does cause practical problems, including incompatibility with the GNU GPL.
    # If you want to use a simple, permissive non-copyleft free software license, it is much better to use the modified BSD license or the X11 license. However, there is no reason not to use programs that have been released under the original BSD license
    CC_SHAREALIKE_3PT0_US = URIRef(_NS["CC-SHAREALIKE-3PT0-US"])
    # Creative Commons Attribution - Share Alike 3.0 United States License
    CCBY_LICENSE = URIRef(_NS["CCBY-LICENSE"])
    # Creative Commons Attribution 2.0 license
    CCBY_ND = URIRef(_NS["CCBY-ND"])
    # Creative Commons Attribution-NoDerivs 3.0 license (a.k.a. CC BY-ND)
    CCBY_SA = URIRef(_NS["CCBY-SA"])
    # Creative Commons Attribution-Sharealike 2.0 license
    CDDL_V1PT0 = URIRef(_NS["CDDL-V1PT0"])
    # A free software license. It has a copyleft with a scope that's similar to the one in the Mozilla Public
    # License, which makes it incompatible with the GNU GPL.
    # This means a module covered by the GPL and a module covered by the CDDL cannot legally be linked together
    CECILL_V2 = URIRef(_NS["CECILL-V2"])
    # A free software license, explicitly compatible with the GNU GPL. The text of the CeCILL uses a couple of
    # biased terms that ought to be avoided: “intellectual property” (see this article) and “protection” (see this article); this decision was unfortunate, because reading the license tends to spread the presuppositions of those terms. However, this does not cause any particular problem for the programs released under the CeCILL. Section 9.4 of the CeCILL commits the program's developers to certain forms of cooperation with the users, if someone attacks the program with a patent. You might look at that as a problem for the developer; however, if you are sure you would want to cooperate with the users in those ways anyway, then it isn't a problem for you
    CLEAR_BSD_LICENSE = URIRef(_NS["CLEAR-BSD-LICENSE"])


# A free software license, compatible with both GPLv2 and GPLv3. It is based on the modified BSD license,
# and adds a term expressly stating it does not grant you any patent licenses.
# Because of this, we encourage you to be careful about using software under this license; you should first
# consider whether the licensor might want to sue you for patent infringement.
# If the developer is disclaiming patent licenses to set up a trap for you, it would be wise to avoid the program
