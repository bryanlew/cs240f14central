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
import java.util.List;
import java.util.Map;

import org.apache.commons.collections15.CollectionUtils;
import org.apache.commons.collections15.Predicate;

public class GroundTruthCompanyAnalytics
{
	public static void main(String[] args) throws IOException
	{
		if(args.length < 3)
		{
			System.out.println("Need 3 arguments, payment-company graph, project edgelist and output file name");
			return;
		}
		File input = new File(args[0]);
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
				if(dictionary.containsKey(v1))
				{
					List<Long> companies = dictionary.get(v1);
					companies.add(v2);
				}
				else
				{
					List<Long> companies = new ArrayList<>();
					companies.add(v2);
					dictionary.put(v1, companies);
				}
			}
		}
		
		reader.close();
		
		input = new File(args[1]);
		reader = new BufferedReader(new FileReader(input));
		List<List<Long>> companies = new ArrayList<List<Long>>();
		BufferedWriter writer = new BufferedWriter(new FileWriter(args[2]));
		BufferedWriter writer2 = new BufferedWriter(new FileWriter("project/size_dist.txt"));
		int maxCommunitySize = 0;
		int minCommunitySize = Integer.MAX_VALUE;
		while((s = reader.readLine())!=null )
		{
			List<Long> companyInCommunity = new ArrayList<Long>();
			String[] docs = s.split("\t");
			for(String doc:docs)
			{
				companyInCommunity.add(Long.valueOf(doc.trim()));
			}
			companies.add(companyInCommunity);
			writer2.write(companies.size() + "\t" + companyInCommunity.size());
			writer2.newLine();
			if(maxCommunitySize < companyInCommunity.size())
			{
				maxCommunitySize = companyInCommunity.size();
			}
			if(minCommunitySize > companyInCommunity.size())
			{
				minCommunitySize = companyInCommunity.size();
			}
		}
		writer2.close();
		reader.close();
		DecimalFormat df = new DecimalFormat("#.0000"); 
		long totalFound = 0;
		long totalInvolvedCOs = 0;
		long totalDetectedCOs = 0;
		for(int i=0;i<companies.size();i++)
		{
			final List<Long> cos = companies.get(i);
			int matchingCommunities = 0;
			List<Long> matchedcids = new ArrayList<Long>();
			List<Long> mds = new ArrayList<Long>();
			for(Long key : dictionary.keySet())
			{
				final List<Long> companiesBase = dictionary.get(key);
				
				int matched = CollectionUtils.countMatches(companiesBase, new Predicate<Long>()
				{
					@Override
               public boolean evaluate(Long arg0)
               {
	               for(Long cid: cos)
	               {
	               	if(cid.longValue()==arg0.longValue())
	               	{
	               		return true;
	               	}
	               }
	               return false;
               }
				});
				
				if(matched==0) continue;
				
				matchingCommunities++;
				matchedcids.addAll(companiesBase);
				mds.add(key);
				
			}
			
			if(matchingCommunities==0)
			{
				writer.write("No Company matched these MDs from ground-truth");
				writer.newLine();
				continue;
			}
			Collection<Long> common = CollectionUtils.intersection(cos, matchedcids);
			totalFound += common.size();
			totalInvolvedCOs += matchedcids.size();
			totalDetectedCOs += cos.size();
			double localRecall = 0.0d;
			double localHM = 0.0d;
			if(!matchedcids.isEmpty())
			{
				localRecall = (double) common.size() / (double) matchedcids.size();
			}
			double localPrecision = (double) common.size() / (double) cos.size();
			if(localRecall!=0)
			{
				localHM = 2.0d / (1.0d/localRecall + 1.0d/localPrecision);
			}
			writer.write("Community: " + i + " found overlap in " + matchingCommunities + ", totalMatches(COs): " + common.size() + 
					", missed(COs): " + (matchedcids.size() - common.size()) + ", CommunityRecall: " + df.format(localRecall)
					+ ", CommunityPrecision: " + df.format(localPrecision) + ", CommunityHM: " + df.format(localHM)
					+ ", MDs Involved in this community: " + mds);
			writer.newLine();
		}
		
		double totalRecall = (double)totalFound / (double)totalInvolvedCOs;
		double totalPrecision = (double)totalFound / (double)totalDetectedCOs;
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
