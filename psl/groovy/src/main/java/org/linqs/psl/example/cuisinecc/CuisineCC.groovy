package org.linqs.psl.example.cuisinecc;

import org.linqs.psl.application.inference.MPEInference;
import org.linqs.psl.config.ConfigBundle;
import org.linqs.psl.config.ConfigManager;
import org.linqs.psl.database.Database;
import org.linqs.psl.database.DatabasePopulator;
import org.linqs.psl.database.DataStore;
import org.linqs.psl.database.Partition;
import org.linqs.psl.database.Queries;
import org.linqs.psl.database.ReadOnlyDatabase;
import org.linqs.psl.database.loading.Inserter;
import org.linqs.psl.database.rdbms.driver.H2DatabaseDriver;
import org.linqs.psl.database.rdbms.driver.H2DatabaseDriver.Type;
import org.linqs.psl.database.rdbms.RDBMSDataStore;
import org.linqs.psl.groovy.PSLModel;
import org.linqs.psl.model.atom.Atom;
import org.linqs.psl.model.predicate.StandardPredicate;
import org.linqs.psl.model.term.ConstantType;
import org.linqs.psl.utils.dataloading.InserterUtils;
import org.linqs.psl.utils.evaluation.printing.AtomPrintStream;
import org.linqs.psl.utils.evaluation.printing.DefaultAtomPrintStream;
import org.linqs.psl.utils.evaluation.statistics.ContinuousPredictionComparator;
import org.linqs.psl.utils.evaluation.statistics.DiscretePredictionComparator;
import org.linqs.psl.utils.evaluation.statistics.MulticlassPredictionComparator;
import org.linqs.psl.utils.evaluation.statistics.DiscretePredictionStatistics;
import org.linqs.psl.utils.evaluation.statistics.MulticlassPredictionStatistics;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import groovy.time.TimeCategory;
import java.nio.file.Paths;

/**
 * A simple Collective Classification example that mirrors the example for the
 * PSL command line tool.
 * This PSL program uses social relationships to determine where people live.
 * It optionally uses a functional constraint that specified that a person
 * can only live in one location.
 *
 * @author Jay Pujara <jay@cs.umd.edu>
 */
public class CuisineCC {
	private static final String PARTITION_OBSERVATIONS = "observations";
	private static final String PARTITION_TARGETS = "targets";
	private static final String PARTITION_TRUTH = "truth";

	private Logger log;
	private DataStore ds;
	private PSLConfig config;
	private PSLModel model;

	/**
	 * Class containing options for configuring the PSL program
	 */
	private class PSLConfig {
		public ConfigBundle cb;

		public String experimentName;
		public String dbPath;
		public String dataPath;
		public String outputPath;

		public boolean sqPotentials = true;
		public Map weightMap = [
				"favoriteCuisine":10,
				"Prior":5
		];
		public boolean useFunctionalConstraint = false;
		public boolean useFunctionalRule = false;

		public PSLConfig(ConfigBundle cb){
			this.cb = cb;

			this.experimentName = cb.getString('experiment.name', 'default');
			this.dbPath = cb.getString('experiment.dbpath', '/tmp');
			this.dataPath = cb.getString('experiment.data.path', '../data');
			this.outputPath = cb.getString('experiment.output.outputdir', Paths.get('output', this.experimentName).toString());

			this.weightMap["favoriteCuisine"] = cb.getInteger('model.weights.knows', weightMap["favoriteCuisine"]);
			this.weightMap["Prior"] = cb.getInteger('model.weights.prior', weightMap["Prior"]);
			this.useFunctionalConstraint = cb.getBoolean('model.constraints.functional', false);
			this.useFunctionalRule = cb.getBoolean('model.rules.functional', false);
		}
	}

	public CuisineCC(ConfigBundle cb) {
		log = LoggerFactory.getLogger(this.class);
		config = new PSLConfig(cb);
		ds = new RDBMSDataStore(new H2DatabaseDriver(Type.Disk, Paths.get(config.dbPath, 'cuisinecc').toString(), true), cb);
		model = new PSLModel(this, ds);
	}

	/**
	 * Defines the logical predicates used by this program
	 */
	private void definePredicates() {
		model.add predicate: "Friend", types: [ConstantType.UniqueID, ConstantType.UniqueID];
		model.add predicate: "favoriteCuisine", types: [ConstantType.UniqueID, ConstantType.UniqueID];
		model.add predicate: "socialInfluenceOnCuisine", types: [ConstantType.UniqueID, ConstantType.UniqueID];
		
        model.add predicate: "usefulUser", types: [ConstantType.UniqueID, ConstantType.UniqueID];
        model.add predicate: "coolUser", types: [ConstantType.UniqueID, ConstantType.UniqueID];
        model.add predicate: "funnyUser", types: [ConstantType.UniqueID, ConstantType.UniqueID];
        model.add predicate: "fansUser", types: [ConstantType.UniqueID, ConstantType.UniqueID];
	}

	/**
	 * Defines the rules used to infer unknown variables in the PSL program
	 */
	private void defineRules() {
		log.info("Defining model rules");

		model.add(
			rule: ( Friend(P1,P2) & favoriteCuisine(P1,C) ) >> socialInfluenceOnCuisine(P2,C),
			squared: config.sqPotentials,
			weight : config.weightMap["favoriteCuisine"]
		);
        
        model.add(
            /*usefulUser(P1,P2) is a stupid hack.*/
			rule: ( Friend(P1,P2) & favoriteCuisine(P1,C) & usefulUser(P1,P1)) >> socialInfluenceOnCuisine(P2,C),
            squared: config.sqPotentials,
            weight: config.weightMap["favoriteCuisine"]
        );
        
        model.add(
            /*coolUser(P1,P2) is a stupid hack.*/
			rule: ( Friend(P1,P2) & favoriteCuisine(P1,C) & coolUser(P1,P1)) >> socialInfluenceOnCuisine(P2,C),
            squared: config.sqPotentials,
            weight: config.weightMap["favoriteCuisine"]
        );
        
        model.add(
            /*funnyUser(P1,P2) is a stupid hack.*/
			rule: ( Friend(P1,P2) & favoriteCuisine(P1,C) & funnyUser(P1,P1)) >> ~socialInfluenceOnCuisine(P2,C),
            squared: config.sqPotentials,
            weight: config.weightMap["favoriteCuisine"]
        );
        
        model.add(
            /*fansUser(P1,P2) is a stupid hack.*/
			rule: ( Friend(P1,P2) & favoriteCuisine(P1,C) & fansUser(P1,P1)) >> socialInfluenceOnCuisine(P2,C),
            squared: config.sqPotentials,
            weight: config.weightMap["favoriteCuisine"]
        );

        model.add(
			rule: ( socialInfluenceOnCuisine(P,C) ) >> favoriteCuisine(P,C),
			squared: config.sqPotentials,
			weight : config.weightMap["favoriteCuisine"]
		);

        model.add(
            rule: ( socialInfluenceOnCuisine(P1,C) & Friend(P1, P2)) >> socialInfluenceOnCuisine(P2,C),
            squared: config.sqPotentials,
            weight : config.weightMap["favoriteCuisine"]
        );

        model.add(
             rule: "socialInfluenceOnCuisine(A, +B) = 1 ."
        );
        
        model.add(
             rule: "favoriteCuisine(A, +B) = 1 ."
        );

		model.add(
			rule: ~favoriteCuisine(P,C),
			squared:config.sqPotentials,
			weight: config.weightMap["Prior"]
		);

		log.debug("model: {}", model);
	}

	/**
	 * Loads the evidence, inference targets, and evaluation data into the DataStore
	 */
	private void loadData(Partition obsPartition, Partition targetsPartition, Partition truthPartition) {
		log.info("Loading data into database");

		Inserter inserter = ds.getInserter(Friend, obsPartition);
		InserterUtils.loadDelimitedData(inserter, Paths.get(config.dataPath, "friends.txt").toString());

		inserter = ds.getInserter(usefulUser, obsPartition);
		InserterUtils.loadDelimitedData(inserter, Paths.get(config.dataPath, "useful.txt").toString());

		inserter = ds.getInserter(coolUser, obsPartition);
		InserterUtils.loadDelimitedData(inserter, Paths.get(config.dataPath, "cool.txt").toString());

        inserter = ds.getInserter(funnyUser, obsPartition);
		InserterUtils.loadDelimitedData(inserter, Paths.get(config.dataPath, "funny.txt").toString());

        inserter = ds.getInserter(fansUser, obsPartition);
		InserterUtils.loadDelimitedData(inserter, Paths.get(config.dataPath, "fans.txt").toString());

        inserter = ds.getInserter(favoriteCuisine, obsPartition);
		InserterUtils.loadDelimitedData(inserter, Paths.get(config.dataPath, "cuisine.txt").toString());

        inserter = ds.getInserter(favoriteCuisine, targetsPartition);
		InserterUtils.loadDelimitedData(inserter, Paths.get(config.dataPath, "favoriteCuisineTarget.txt").toString());

        inserter = ds.getInserter(socialInfluenceOnCuisine, targetsPartition);
		InserterUtils.loadDelimitedData(inserter, Paths.get(config.dataPath, "socialInfluenceTarget.txt").toString());

		inserter = ds.getInserter(favoriteCuisine, truthPartition);
		InserterUtils.loadDelimitedData(inserter, Paths.get(config.dataPath, "truth.txt").toString());
	}

	/**
	 * Performs inference using the defined model and evidence, storing results in DataStore
	 */
	private void runInference(Partition obsPartition, Partition targetsPartition) {
		log.info("Starting inference");

		Date infStart = new Date();
		HashSet closed = new HashSet<StandardPredicate>([Friend, usefulUser, coolUser, funnyUser, fansUser]);
		Database inferDB = ds.getDatabase(targetsPartition, closed, obsPartition);
		MPEInference mpe = new MPEInference(model, inferDB, config.cb);
		mpe.mpeInference();

		inferDB.close();
		mpe.close();

		log.info("Finished inference in {}", TimeCategory.minus(new Date(), infStart));
	}

	/**
	 * Writes the inference outputs to a file
	 */
	private void writeOutput(Partition targetsPartition) {
		Database resultsDB = ds.getDatabase(targetsPartition);
		PrintStream ps = new PrintStream(new File(Paths.get(config.outputPath, "favoriteCuisine.txt").toString()));
		AtomPrintStream aps = new DefaultAtomPrintStream(ps);
		Set atomSet = Queries.getAllAtoms(resultsDB, favoriteCuisine);
		for (Atom a : atomSet) {
			aps.printAtom(a);
		}
        aps.close();
		ps.close();
		
        ps = new PrintStream(new File(Paths.get(config.outputPath, "socialInfluence.txt").toString()));
		aps = new DefaultAtomPrintStream(ps);
		atomSet = Queries.getAllAtoms(resultsDB, socialInfluenceOnCuisine);
		for (Atom a : atomSet) {
			aps.printAtom(a);
		}
        aps.close();
        ps.close();
        resultsDB.close();
	}

	/**
	 * Evaluates the results of inference versus expected truth values
	 */
	private void evalResults(Partition targetsPartition, Partition truthPartition) {
		Database resultsDB = ds.getDatabase(targetsPartition, [favoriteCuisine] as Set);
		Database truthDB = ds.getDatabase(truthPartition, [favoriteCuisine] as Set);
		'''MulticlassPredictionComparator mpc = new MulticlassPredictionComparator(resultsDB);'''
        DiscretePredictionComparator dpc = new DiscretePredictionComparator(resultsDB);
		dpc.setBaseline(truthDB);
        DiscretePredictionStatistics stats = dpc.compare(favoriteCuisine);
		'''MulticlassPredictionStatistics stats = mpc.compare(favoriteCuisine);'''
		'''log.info(
        
				"Stats: confusion matrix {}, recall {}, accuracy {}, F1 {}",
				stats.getConfusionMatrix(),
                stats.getAccuracy()
        );'''
        log.info(
        
				"Stats: precision {}, recall {}, accuracy {}, F1 {}",
				stats.getPrecision(DiscretePredictionStatistics.BinaryClass.POSITIVE),
				stats.getRecall(DiscretePredictionStatistics.BinaryClass.POSITIVE),
                stats.getAccuracy(),
                stats.getF1(DiscretePredictionStatistics.BinaryClass.POSITIVE)
        );

		resultsDB.close();
		truthDB.close();
	}


	/**
	 * Runs the PSL program using configure options - defines a model, loads data,
	 * performs inferences, writes output to files, evaluates results
	 */
	public void run() {
		log.info("Running experiment {}", config.experimentName);

		Partition obsPartition = ds.getPartition(PARTITION_OBSERVATIONS);
		Partition targetsPartition = ds.getPartition(PARTITION_TARGETS);
		Partition truthPartition = ds.getPartition(PARTITION_TRUTH);

		definePredicates();
		defineRules();
		loadData(obsPartition, targetsPartition, truthPartition);
		runInference(obsPartition, targetsPartition);
		writeOutput(targetsPartition);
		evalResults(targetsPartition, truthPartition);

		ds.close();
	}

	/**
	 * Populates the ConfigBundle for this PSL program using arguments specified on
	 * the command line
	 * @param args - Command line arguments supplied during program invocation
	 * @return ConfigBundle with the appropriate properties set
	 */
	public static ConfigBundle populateConfigBundle(String[] args) {
		ConfigBundle cb = ConfigManager.getManager().getBundle("cuisinecc");
		if (args.length > 0) {
			cb.setProperty('experiment.data.path', args[0]);
		}
		return cb;
	}

	/**
	 * Runs the PSL program from the command line with specified arguments
	 * @param args - Arguments for program options
	 */
	public static void main(String[] args){
		ConfigBundle cb = populateConfigBundle(args);
		CuisineCC cc = new CuisineCC(cb);
		cc.run();
	}
}
