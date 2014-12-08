package edu.stanford.cs224w.project;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.commons.collections15.CollectionUtils;
import org.apache.commons.collections15.Predicate;

public class GroundTruthComparator
{
	public static void main(String[] args) throws IOException
	{
		if(args.length < 3)
		{
			System.out.println("Need 3 arguments, payment-company graph, project edgelist and output file name");
			return;
		}
		File input = new File(args[0]);//"project/minProportions/minProportion_doc_0.1_co_0.0_payment_graph_physician_company.csv");
		BufferedReader reader = new BufferedReader(new FileReader(input));
		Map<Long, List<Long>> dictionary= new HashMap<Long, List<Long>>();
		int line = 0;
		String s = null;
		int paymentThreshold = 0;
		while((s = reader.readLine())!=null )
		{
			String[] inputs = s.split("\t");
			String npi = inputs[0];
			String companyId = inputs[1];
			String amount = "0";
			if(inputs.length > 2)
			{
				amount = inputs[2];
			}
			if(line++==0)
			{
				continue;
			}
			long v1 = 0l;
			long v2 = 0l;
			double w1 = 0d;
			try
			{
				v1 = Long.valueOf(npi.trim());
			}
			catch(Exception e){}
			try
			{
				v2 = Long.valueOf(companyId.trim());
			}
			catch(Exception e){}
			try
			{
				w1 = Double.valueOf(amount.trim());
			}
			catch(Exception e){}
			if(w1 >= paymentThreshold)
			{
				if(dictionary.containsKey(v2))
				{
					List<Long> providers = dictionary.get(v2);
					providers.add(v1);
				}
				else
				{
					List<Long> providers = new ArrayList<>();
					providers.add(v1);
					dictionary.put(v2, providers);
				}
			}
		}
		
		reader.close();
		
//		BufferedWriter writer = new BufferedWriter(new FileWriter("company_docs_0.txt"));
//		for(Long key : dictionary.keySet())
//		{
//			List<Long> providers = dictionary.get(key);
//			writer.write(key + "\t" + providers);
//			writer.newLine();
//			writer.flush();
//		}
//		writer.close();
		
		input = new File(args[1]);
		reader = new BufferedReader(new FileReader(input));
		List<List<Long>> doctors = new ArrayList<List<Long>>();
		BufferedWriter writer = new BufferedWriter(new FileWriter(args[2]));
		BufferedWriter writer2 = new BufferedWriter(new FileWriter("project/size_dist.txt"));
		int maxCommunitySize = 0;
		int minCommunitySize = Integer.MAX_VALUE;
		while((s = reader.readLine())!=null )
		{
			List<Long> docInCommunity = new ArrayList<Long>();
			String[] docs = s.split("\t");
			for(String doc:docs)
			{
				docInCommunity.add(Long.valueOf(doc.trim()));
			}
			doctors.add(docInCommunity);
			writer2.write(doctors.size() + "\t" + docInCommunity.size());
			writer2.newLine();
			if(maxCommunitySize < docInCommunity.size())
			{
				maxCommunitySize = docInCommunity.size();
			}
			if(minCommunitySize > docInCommunity.size())
			{
				minCommunitySize = docInCommunity.size();
			}
		}
		writer2.close();
		reader.close();
		DecimalFormat df = new DecimalFormat("#.0000"); 
		long totalFound = 0;
		long totalInvolvedDocs = 0;
		long totalDetectedDocs = 0;
		final long specialMatchNPI = 78006l; 
		Set<Long> specialMatchCompany = new HashSet();
		for(int i=0;i<doctors.size();i++)
		{
			final List<Long> docs = doctors.get(i);
			int matchingCommunities = 0;
			List<Long> matchedNpis = new ArrayList<Long>();
			List<Long> companyIds = new ArrayList<Long>();
			for(Long key : dictionary.keySet())
			{
				final List<Long> providers = dictionary.get(key);
				
				int matched = CollectionUtils.countMatches(providers, new Predicate<Long>()
				{
					@Override
               public boolean evaluate(Long arg0)
               {
	               for(Long npi: docs)
	               {
	               	if(npi.longValue()==arg0.longValue())
	               	{
	               		return true;
	               	}
	               }
	               return false;
               }
				});
				
				int matched2 = CollectionUtils.countMatches(providers, new Predicate<Long>()
				{
					@Override
               public boolean evaluate(Long arg0)
               {
	               for(Long npi: docs)
	               {
	               	if(npi.longValue()==specialMatchNPI && npi.longValue()==arg0.longValue())
	               	{
	               		return true;
	               	}
	               }
	               return false;
               }
				});
				if(matched2 > 0)
				{
					specialMatchCompany.add(key);
				}
				if(matched==0) continue;
				
				matchingCommunities++;
				matchedNpis.addAll(providers);
				companyIds.add(key);
				
//				writer.write("Community: " + i + " Matched: " + matched + " CompanyID:" + key + " mismatched(-ve means ground truth had smaller size): " + (providers.size() - docs.size()));
//				writer.newLine();
			}
			
			if(matchingCommunities==0)
			{
				writer.write("No Company matched these MDs from ground-truth");
				writer.newLine();
				continue;
			}
			Collection<Long> common = CollectionUtils.intersection(docs, matchedNpis);
			totalFound += common.size();
			totalInvolvedDocs += matchedNpis.size();
			totalDetectedDocs += docs.size();
			double localRecall = 0.0d;
			double localHM = 0.0d;
			if(!matchedNpis.isEmpty())
			{
				localRecall = (double) common.size() / (double) matchedNpis.size();
			}
			double localPrecision = (double) common.size() / (double) docs.size();
			if(localRecall!=0)
			{
				localHM = 2.0d / (1.0d/localRecall + 1.0d/localPrecision);
			}
			writer.write("Community: " + i + " found overlap in " + matchingCommunities + ", totalMatches(MDs): " + common.size() + 
					", missed(MDs): " + (matchedNpis.size() - common.size()) + ", CommunityRecall: " + df.format(localRecall)
					+ ", CommunityPrecision: " + df.format(localPrecision) + ", CommunityHM: " + df.format(localHM)
					+ ", Companies Involved in this community: " + companyIds);
			writer.newLine();
		}
		
		System.out.println(specialMatchCompany.size() + " : " + specialMatchCompany);
		
		double totalRecall = (double)totalFound / (double)totalInvolvedDocs;
		double totalPrecision = (double)totalFound / (double)totalDetectedDocs;
		double totalHM = 2.0d / ((1.0d/totalRecall) + (1.0d/totalPrecision));
		writer.write("Total Recall: " + df.format(totalRecall));
		writer.newLine();
		writer.write("Total Precision: " + df.format(totalPrecision));
		writer.newLine();
		writer.write("Total HM: " + df.format(totalHM));
		writer.newLine();
		writer.write("MaxCommunitySize: " + maxCommunitySize + ", " + "MinCommunitySize: " + minCommunitySize);
		writer.close();
		
	}

}
